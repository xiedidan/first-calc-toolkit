"""
模型版本导入服务
"""
from typing import Optional, Dict, List, Any
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.model_version import ModelVersion
from app.models.model_node import ModelNode
from app.models.calculation_workflow import CalculationWorkflow
from app.models.calculation_step import CalculationStep
from app.models.model_version_import import ModelVersionImport
from app.models.data_source import DataSource
from app.schemas.model_version import ModelVersionImportRequest


class ModelVersionImportService:
    """模型版本导入服务类"""

    def __init__(self, db: Session):
        self.db = db
        self.warnings: List[str] = []

    def import_model_version(
        self,
        request: ModelVersionImportRequest,
        target_hospital_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """
        导入模型版本
        
        Args:
            request: 导入请求
            target_hospital_id: 目标医疗机构ID
            user_id: 导入用户ID
            
        Returns:
            导入结果字典，包含新版本ID和统计信息
        """
        self.warnings = []
        
        try:
            # 1. 验证源版本存在
            source_version = self.db.query(ModelVersion).filter(
                ModelVersion.id == request.source_version_id
            ).first()
            if not source_version:
                raise ValueError("源版本不存在")
            
            # 2. 验证版本号唯一性
            existing = self.db.query(ModelVersion).filter(
                ModelVersion.hospital_id == target_hospital_id,
                ModelVersion.version == request.version
            ).first()
            if existing:
                raise ValueError("版本号已存在")
            
            # 3. 创建新版本
            new_version = ModelVersion(
                hospital_id=target_hospital_id,
                version=request.version,
                name=request.name,
                description=request.description,
                is_active=False
            )
            self.db.add(new_version)
            self.db.flush()  # 获取新版本ID
            
            # 4. 复制模型节点
            node_count = self._copy_nodes(source_version.id, new_version.id)
            
            # 5. 可选：复制计算流程
            workflow_count = 0
            step_count = 0
            if request.import_type == "with_workflows":
                workflow_count, step_count = self._copy_workflows(
                    source_version.id,
                    new_version.id,
                    target_hospital_id
                )
            
            # 6. 记录导入历史
            statistics = {
                "node_count": node_count,
                "workflow_count": workflow_count,
                "step_count": step_count
            }
            self._record_import_history(
                target_version_id=new_version.id,
                source_version_id=source_version.id,
                source_hospital_id=source_version.hospital_id,
                import_type=request.import_type,
                imported_by=user_id,
                statistics=statistics
            )
            
            # 7. 提交事务
            self.db.commit()
            
            return {
                "id": new_version.id,
                "version": new_version.version,
                "name": new_version.name,
                "statistics": statistics,
                "warnings": self.warnings
            }
            
        except Exception as e:
            self.db.rollback()
            raise e

    def _copy_nodes(self, source_version_id: int, target_version_id: int) -> int:
        """
        复制模型节点（递归）
        
        Args:
            source_version_id: 源版本ID
            target_version_id: 目标版本ID
            
        Returns:
            复制的节点数量
        """
        # 获取源版本的所有根节点
        root_nodes = self.db.query(ModelNode).filter(
            ModelNode.version_id == source_version_id,
            ModelNode.parent_id.is_(None)
        ).order_by(ModelNode.sort_order).all()
        
        node_count = 0
        for node in root_nodes:
            node_count += self._copy_node_recursive(node, target_version_id, None)
        
        return node_count

    def _copy_node_recursive(
        self,
        source_node: ModelNode,
        target_version_id: int,
        target_parent_id: Optional[int]
    ) -> int:
        """
        递归复制节点
        
        Args:
            source_node: 源节点
            target_version_id: 目标版本ID
            target_parent_id: 目标父节点ID
            
        Returns:
            复制的节点数量（包括子节点）
        """
        # 创建新节点
        new_node = ModelNode(
            version_id=target_version_id,
            parent_id=target_parent_id,
            sort_order=source_node.sort_order,
            name=source_node.name,
            code=source_node.code,
            node_type=source_node.node_type,
            is_leaf=source_node.is_leaf,
            calc_type=source_node.calc_type,
            weight=source_node.weight,
            unit=source_node.unit,
            business_guide=source_node.business_guide,
            script=source_node.script,
            rule=source_node.rule,
            orientation_rule_ids=source_node.orientation_rule_ids  # 复制导向规则ID列表
        )
        self.db.add(new_node)
        self.db.flush()  # 获取新节点ID
        
        count = 1
        
        # 递归复制子节点
        for child in source_node.children:
            count += self._copy_node_recursive(child, target_version_id, new_node.id)
        
        return count

    def _copy_workflows(
        self,
        source_version_id: int,
        target_version_id: int,
        target_hospital_id: int
    ) -> tuple[int, int]:
        """
        复制计算流程和步骤
        
        Args:
            source_version_id: 源版本ID
            target_version_id: 目标版本ID
            target_hospital_id: 目标医疗机构ID
            
        Returns:
            (workflow_count, step_count) 复制的流程数量和步骤数量
        """
        # 获取源版本的所有计算流程
        source_workflows = self.db.query(CalculationWorkflow).filter(
            CalculationWorkflow.version_id == source_version_id
        ).all()
        
        workflow_count = 0
        step_count = 0
        
        for source_workflow in source_workflows:
            # 创建新流程
            new_workflow = CalculationWorkflow(
                version_id=target_version_id,
                name=source_workflow.name,
                description=source_workflow.description,
                is_active=source_workflow.is_active
            )
            self.db.add(new_workflow)
            self.db.flush()  # 获取新流程ID
            
            workflow_count += 1
            
            # 复制流程的所有步骤
            source_steps = self.db.query(CalculationStep).filter(
                CalculationStep.workflow_id == source_workflow.id
            ).order_by(CalculationStep.sort_order).all()
            
            for source_step in source_steps:
                # 处理数据源引用
                data_source_id = source_step.data_source_id
                if data_source_id:
                    # 检查数据源是否在目标医疗机构存在
                    data_source_exists = self.db.query(DataSource).filter(
                        DataSource.id == data_source_id,
                        DataSource.hospital_id == target_hospital_id
                    ).first()
                    
                    if not data_source_exists:
                        # 数据源不存在，设为NULL并记录警告
                        data_source_id = None
                        self.warnings.append(
                            f"计算步骤 '{source_step.name}' 引用的数据源在目标医疗机构不存在，已设置为使用默认数据源"
                        )
                
                # 创建新步骤
                new_step = CalculationStep(
                    workflow_id=new_workflow.id,
                    name=source_step.name,
                    description=source_step.description,
                    code_type=source_step.code_type,
                    code_content=source_step.code_content,
                    data_source_id=data_source_id,
                    sort_order=source_step.sort_order,
                    is_enabled=source_step.is_enabled
                )
                self.db.add(new_step)
                step_count += 1
        
        return workflow_count, step_count

    def _record_import_history(
        self,
        target_version_id: int,
        source_version_id: int,
        source_hospital_id: int,
        import_type: str,
        imported_by: int,
        statistics: Dict[str, Any]
    ):
        """
        记录导入历史
        
        Args:
            target_version_id: 目标版本ID
            source_version_id: 源版本ID
            source_hospital_id: 源医疗机构ID
            import_type: 导入类型
            imported_by: 导入用户ID
            statistics: 导入统计信息
        """
        import_record = ModelVersionImport(
            target_version_id=target_version_id,
            source_version_id=source_version_id,
            source_hospital_id=source_hospital_id,
            import_type=import_type,
            imported_by=imported_by,
            statistics=statistics
        )
        self.db.add(import_record)
