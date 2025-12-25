/**
 * 系统菜单配置
 * 统一定义，用于：
 * 1. Layout.vue 菜单渲染
 * 2. 角色权限配置
 */

export interface MenuItem {
  path: string
  name: string
  icon?: string
  disabled?: boolean  // 是否禁用（规划中的功能）
  adminOnly?: boolean // 仅管理员可见
  maintainerOnly?: boolean // 仅维护者可见
  children?: MenuItem[]
}

export const SYSTEM_MENUS: MenuItem[] = [
  { path: '/dashboard', name: '首页', icon: 'HomeFilled' },
  { path: '/data-template-publish', name: '数据模板发布', icon: 'Grid' },
  {
    path: '/data-quality', name: '数据质量报告', icon: 'DocumentChecked',
    children: [
      { path: '/data-issues', name: '数据问题记录' },
    ]
  },
  {
    path: '/intelligent-classification', name: '智能分类分级', icon: 'Operation',
    children: [
      { path: '/classification-tasks', name: '医技分类任务' },
      { path: '/classification-plans', name: '分类预案管理' },
    ]
  },
  {
    path: '/model', name: '评估模型管理', icon: 'Document',
    children: [
      { path: '/model-versions', name: '模型版本管理' },
      { path: '/dimension-items', name: '维度目录管理' },
      { path: '/cost-benchmarks', name: '成本基准管理' },
      { path: '/discipline-rules', name: '学科规则管理' },
      { path: '/calculation-workflows', name: '计算流程管理' },
    ]
  },
  {
    path: '/orientation', name: '业务导向管理', icon: 'Guide',
    children: [
      { path: '/orientation-rules', name: '导向规则管理' },
      { path: '/orientation-benchmarks', name: '导向基准管理' },
      { path: '/orientation-ladders', name: '导向阶梯管理' },
    ]
  },
  { path: '/calculation-tasks', name: '计算任务管理', icon: 'Clock' },
  { path: '/results', name: '业务价值报表', icon: 'DataAnalysis' },
  { path: '/adv-modeling', name: 'ADV自动建模', icon: 'MagicStick', disabled: true },
  {
    path: '/intelligent-query', name: '智能问数系统', icon: 'ChatDotRound',
    children: [
      { path: '/smart-data-qa', name: '智能数据问答' },
      { path: '/metric-assets', name: '指标资产管理' },
    ]
  },
  {
    path: '/operation-analysis', name: '运营分析报告', icon: 'TrendCharts',
    children: [
      { path: '/report-view', name: '分析报告查看' },
      { path: '/report-management', name: '分析报告管理', adminOnly: true },
    ]
  },
  {
    path: '/base-data', name: '基础数据管理', icon: 'FolderOpened',
    children: [
      { path: '/departments', name: '科室对照管理' },
      { path: '/charge-items', name: '收费项目管理' },
      { path: '/cost-reports', name: '成本报表管理' },
      { path: '/reference-values', name: '参考价值管理' },
      { path: '/data-templates', name: '数据模板管理', adminOnly: true },
    ]
  },
  { path: '/data-sources', name: '数据源管理', icon: 'Connection' },
  {
    path: '/system', name: '系统设置', icon: 'Setting',
    children: [
      { path: '/system-settings', name: '参数管理' },
      { path: '/users', name: '用户管理', adminOnly: true },
      { path: '/roles', name: '用户角色管理', adminOnly: true },
      { path: '/ai-config', name: 'AI接口管理', maintainerOnly: true },
      { path: '/hospitals', name: '医疗机构管理', adminOnly: true },
    ]
  },
]

/**
 * 获取用于权限配置的菜单树（过滤掉仅管理员/维护者的菜单，移除disabled属性）
 */
export function getPermissionMenuTree(): MenuItem[] {
  function filterMenu(menus: MenuItem[]): MenuItem[] {
    return menus
      .filter(m => !m.adminOnly && !m.maintainerOnly)
      .map(m => {
        const { disabled, ...rest } = m  // 移除disabled属性
        return {
          ...rest,
          children: m.children ? filterMenu(m.children) : undefined
        }
      })
  }
  return filterMenu(SYSTEM_MENUS)
}

/**
 * 获取所有菜单路径（用于全选）
 */
export function getAllMenuPaths(menus: MenuItem[] = SYSTEM_MENUS): string[] {
  const paths: string[] = []
  for (const menu of menus) {
    if (!menu.adminOnly && !menu.maintainerOnly) {
      paths.push(menu.path)
      if (menu.children) {
        paths.push(...getAllMenuPaths(menu.children))
      }
    }
  }
  return paths
}
