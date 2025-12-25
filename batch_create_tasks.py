"""
批量创建计算任务并顺次执行

用法示例:
    python batch_create_tasks.py --url http://123.456.78.432:12344 --start 2024-11 --end 2025-10 --version-id 1 --workflow-id 31
    python batch_create_tasks.py --url http://localhost:8000 --start 2024-11 --end 2024-12  # 使用激活版本和默认流程
    python batch_create_tasks.py --url http://localhost:8000 --periods 2024-11,2024-12,2025-01  # 指定具体月份
"""
import argparse
import requests
import time
import sys
from datetime import datetime
from typing import List, Optional


def parse_args():
    parser = argparse.ArgumentParser(description="批量创建计算任务并顺次执行")
    parser.add_argument("--url", required=True, help="后端API地址，如 http://localhost:8000")
    parser.add_argument("--start", help="开始年月，格式 YYYY-MM，如 2024-11")
    parser.add_argument("--end", help="结束年月，格式 YYYY-MM，如 2025-10")
    parser.add_argument("--periods", help="指定具体月份列表，逗号分隔，如 2024-11,2024-12,2025-01")
    parser.add_argument("--version-id", type=int, help="模型版本ID，不指定则使用激活版本")
    parser.add_argument("--workflow-id", type=int, help="计算流程ID，不指定则使用版本的第一个流程")
    parser.add_argument("--hospital-id", type=int, default=1, help="医疗机构ID，默认为1")
    parser.add_argument("--username", default="admin", help="登录用户名，默认admin")
    parser.add_argument("--password", default="admin123", help="登录密码，默认admin123")
    parser.add_argument("--timeout", type=int, default=1800, help="单个任务超时时间（秒），默认1800")
    parser.add_argument("--poll-interval", type=int, default=10, help="轮询间隔（秒），默认10")
    parser.add_argument("--dry-run", action="store_true", help="仅显示将要创建的任务，不实际执行")
    return parser.parse_args()


def generate_periods(start: str, end: str) -> List[str]:
    """生成从start到end的所有月份列表"""
    periods = []
    start_year, start_month = map(int, start.split("-"))
    end_year, end_month = map(int, end.split("-"))
    
    year, month = start_year, start_month
    while (year, month) <= (end_year, end_month):
        periods.append(f"{year}-{month:02d}")
        month += 1
        if month > 12:
            month = 1
            year += 1
    
    return periods


class TaskRunner:
    def __init__(self, base_url: str, hospital_id: int, username: str, password: str,
                 timeout: int = 1800, poll_interval: int = 10):
        self.base_url = base_url.rstrip("/")
        self.api_url = f"{self.base_url}/api/v1"
        self.hospital_id = hospital_id
        self.username = username
        self.password = password
        self.timeout = timeout
        self.poll_interval = poll_interval
        self.token = None
        self.headers = {}
    
    def login(self) -> bool:
        """登录获取token"""
        print(f"正在登录 {self.base_url}...")
        try:
            response = requests.post(
                f"{self.api_url}/auth/login",
                json={"username": self.username, "password": self.password},
                timeout=30
            )
            if response.status_code == 200:
                self.token = response.json()["access_token"]
                self.headers = {
                    "Authorization": f"Bearer {self.token}",
                    "X-Hospital-ID": str(self.hospital_id)
                }
                print("登录成功")
                return True
            else:
                print(f"登录失败: {response.status_code} - {response.text}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"登录请求失败: {e}")
            return False
    
    def get_active_version(self) -> Optional[int]:
        """获取激活的模型版本ID"""
        try:
            response = requests.get(
                f"{self.api_url}/model-versions",
                headers=self.headers,
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                versions = data.get("items", []) if isinstance(data, dict) else data
                for v in versions:
                    if v.get("is_active"):
                        print(f"找到激活版本: ID={v['id']}, 名称={v.get('name', 'N/A')}")
                        return v["id"]
            print("未找到激活的模型版本")
            return None
        except requests.exceptions.RequestException as e:
            print(f"获取模型版本失败: {e}")
            return None
    
    def get_workflow_id(self, version_id: int) -> Optional[int]:
        """获取指定版本的计算流程ID"""
        try:
            response = requests.get(
                f"{self.api_url}/calculation-workflows",
                headers=self.headers,
                params={"version_id": version_id},
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                workflows = data.get("items", []) if isinstance(data, dict) else data
                if workflows:
                    wf = workflows[0]
                    print(f"找到计算流程: ID={wf['id']}, 名称={wf.get('name', 'N/A')}")
                    return wf["id"]
            print(f"未找到版本 {version_id} 的计算流程")
            return None
        except requests.exceptions.RequestException as e:
            print(f"获取计算流程失败: {e}")
            return None
    
    def create_task(self, version_id: int, workflow_id: int, period: str) -> Optional[dict]:
        """创建计算任务"""
        try:
            response = requests.post(
                f"{self.api_url}/calculation/tasks",
                headers=self.headers,
                json={
                    "model_version_id": version_id,
                    "workflow_id": workflow_id,
                    "period": period,
                    "description": f"{period} 批量计算任务"
                },
                timeout=120
            )
            if response.status_code == 200:
                return response.json()
            else:
                print(f"  创建任务失败: {response.status_code} - {response.text}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"  创建任务请求失败: {e}")
            return None
    
    def check_task_status(self, task_id: str) -> Optional[dict]:
        """检查任务状态"""
        try:
            response = requests.get(
                f"{self.api_url}/calculation/tasks/{task_id}",
                headers=self.headers,
                timeout=30
            )
            if response.status_code == 200:
                return response.json()
            return None
        except requests.exceptions.RequestException:
            return None
    
    def wait_for_task(self, task_id: str) -> tuple:
        """等待任务完成，返回 (success, final_status, error_message)"""
        start_time = time.time()
        last_progress = -1
        
        while time.time() - start_time < self.timeout:
            task = self.check_task_status(task_id)
            if task:
                status = task.get("status", "unknown")
                progress = float(task.get("progress", 0))
                
                # 只在进度变化时打印
                if progress != last_progress:
                    elapsed = int(time.time() - start_time)
                    print(f"    [{elapsed}s] 状态: {status}, 进度: {progress:.1f}%")
                    last_progress = progress
                
                if status == "completed":
                    return True, status, None
                elif status == "failed":
                    error_msg = task.get("error_message", "未知错误")
                    return False, status, error_msg
                elif status == "cancelled":
                    return False, status, "任务已取消"
            
            time.sleep(self.poll_interval)
        
        return False, "timeout", f"任务超时（{self.timeout}秒）"
    
    def run_tasks(self, periods: List[str], version_id: int, workflow_id: int, dry_run: bool = False):
        """批量执行任务"""
        print(f"\n{'='*60}")
        print(f"任务配置:")
        print(f"  后端地址: {self.base_url}")
        print(f"  医疗机构ID: {self.hospital_id}")
        print(f"  模型版本ID: {version_id}")
        print(f"  计算流程ID: {workflow_id}")
        print(f"  任务数量: {len(periods)}")
        print(f"  月份列表: {', '.join(periods)}")
        print(f"  单任务超时: {self.timeout}秒")
        print(f"{'='*60}\n")
        
        if dry_run:
            print("[DRY RUN] 仅显示将要创建的任务，不实际执行")
            for i, period in enumerate(periods, 1):
                print(f"  [{i}/{len(periods)}] {period}")
            return
        
        results = []
        total_start = time.time()
        
        for i, period in enumerate(periods, 1):
            print(f"\n[{i}/{len(periods)}] 创建 {period} 的计算任务...")
            task_start = time.time()
            
            task = self.create_task(version_id, workflow_id, period)
            if task:
                task_id = task.get("task_id")
                print(f"  任务已创建: {task_id}")
                print(f"  等待任务完成...")
                
                success, final_status, error_msg = self.wait_for_task(task_id)
                task_duration = int(time.time() - task_start)
                
                results.append({
                    "period": period,
                    "task_id": task_id,
                    "success": success,
                    "status": final_status,
                    "error": error_msg,
                    "duration": task_duration
                })
                
                if success:
                    print(f"  ✓ {period} 计算完成 (耗时 {task_duration}秒)")
                else:
                    print(f"  ✗ {period} 计算失败: {error_msg}")
            else:
                results.append({
                    "period": period,
                    "task_id": None,
                    "success": False,
                    "status": "create_failed",
                    "error": "创建任务失败",
                    "duration": 0
                })
                print(f"  ✗ {period} 创建失败")
        
        # 汇总结果
        total_duration = int(time.time() - total_start)
        self._print_summary(results, total_duration)
    
    def _print_summary(self, results: List[dict], total_duration: int):
        """打印执行结果汇总"""
        print(f"\n{'='*60}")
        print("执行结果汇总")
        print(f"{'='*60}")
        
        success_count = sum(1 for r in results if r["success"])
        fail_count = len(results) - success_count
        
        print(f"总计: {len(results)} 个任务")
        print(f"成功: {success_count} 个")
        print(f"失败: {fail_count} 个")
        print(f"总耗时: {total_duration}秒 ({total_duration//60}分{total_duration%60}秒)")
        print()
        
        # 详细列表
        print("详细结果:")
        for r in results:
            status_icon = "✓" if r["success"] else "✗"
            task_info = r["task_id"][:8] + "..." if r["task_id"] else "N/A"
            duration_info = f"{r['duration']}s" if r["duration"] > 0 else "-"
            
            if r["success"]:
                print(f"  {status_icon} {r['period']}: {task_info} ({duration_info})")
            else:
                print(f"  {status_icon} {r['period']}: {r['error']} ({duration_info})")
        
        # 失败任务详情
        failed = [r for r in results if not r["success"]]
        if failed:
            print(f"\n失败任务详情:")
            for r in failed:
                print(f"  - {r['period']}: {r['error']}")
                if r["task_id"]:
                    print(f"    任务ID: {r['task_id']}")


def main():
    args = parse_args()
    
    # 确定要处理的月份列表
    if args.periods:
        periods = [p.strip() for p in args.periods.split(",")]
    elif args.start and args.end:
        periods = generate_periods(args.start, args.end)
    else:
        print("错误: 必须指定 --start 和 --end，或者 --periods")
        sys.exit(1)
    
    if not periods:
        print("错误: 没有有效的月份")
        sys.exit(1)
    
    # 创建任务执行器
    runner = TaskRunner(
        base_url=args.url,
        hospital_id=args.hospital_id,
        username=args.username,
        password=args.password,
        timeout=args.timeout,
        poll_interval=args.poll_interval
    )
    
    # 登录
    if not runner.login():
        sys.exit(1)
    
    # 确定模型版本ID
    version_id = args.version_id
    if not version_id:
        print("\n获取激活的模型版本...")
        version_id = runner.get_active_version()
        if not version_id:
            print("错误: 未找到激活的模型版本，请使用 --version-id 指定")
            sys.exit(1)
    else:
        print(f"\n使用指定的模型版本ID: {version_id}")
    
    # 确定计算流程ID
    workflow_id = args.workflow_id
    if not workflow_id:
        print("\n获取计算流程...")
        workflow_id = runner.get_workflow_id(version_id)
        if not workflow_id:
            print("错误: 未找到计算流程，请使用 --workflow-id 指定")
            sys.exit(1)
    else:
        print(f"\n使用指定的计算流程ID: {workflow_id}")
    
    # 执行任务
    runner.run_tasks(periods, version_id, workflow_id, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
