import * as modelApi from '@/api/model'
import ModelRules from '@/views/ModelRules.vue'
import ModelVersions from '@/views/ModelVersions.vue'
import { mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createRouter, createWebHistory } from 'vue-router'

// Mock API
vi.mock('@/api/model', () => ({
  getModelVersion: vi.fn(),
  getModelNodes: vi.fn(),
  getModelVersions: vi.fn()
}))

// Mock router
const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/model-versions', name: 'ModelVersions', component: ModelVersions },
    { path: '/model-rules/:versionId', name: 'ModelRules', component: ModelRules }
  ]
})

describe('模型规则展示功能测试', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('1. 从版本列表导航到规则展示页面', () => {
    it('应该在版本列表显示"查看规则"按钮', async () => {
      vi.mocked(modelApi.getModelVersions).mockResolvedValue({
        items: [
          { id: 1, version: 'v1.0', name: '测试版本', is_active: true, created_at: '2025-01-01' }
        ],
        total: 1
      })

      const wrapper = mount(ModelVersions, {
        global: {
          plugins: [router]
        }
      })

      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      const viewRulesButton = wrapper.find('[type="info"]')
      expect(viewRulesButton.exists()).toBe(true)
      expect(viewRulesButton.text()).toContain('查看规则')
    })

    it('点击"查看规则"按钮应该导航到规则展示页面', async () => {
      vi.mocked(modelApi.getModelVersions).mockResolvedValue({
        items: [
          { id: 1, version: 'v1.0', name: '测试版本', is_active: true, created_at: '2025-01-01' }
        ],
        total: 1
      })

      const wrapper = mount(ModelVersions, {
        global: {
          plugins: [router]
        }
      })

      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      const pushSpy = vi.spyOn(router, 'push')
      const viewRulesButton = wrapper.find('[type="info"]')
      await viewRulesButton.trigger('click')

      expect(pushSpy).toHaveBeenCalledWith({
        name: 'ModelRules',
        params: { versionId: 1 }
      })
    })
  })

  describe('2. 规则内容的正确显示（包括换行、空格）', () => {
    it('应该正确显示包含换行的规则内容', async () => {
      const ruleWithNewlines = '第一行规则\n第二行规则\n第三行规则'
      
      vi.mocked(modelApi.getModelVersion).mockResolvedValue({
        id: 1,
        version: 'v1.0',
        name: '测试版本',
        is_active: true
      })

      vi.mocked(modelApi.getModelNodes).mockResolvedValue({
        items: [
          {
            id: 1,
            code: 'TEST001',
            name: '测试节点',
            node_type: 'sequence',
            rule: ruleWithNewlines,
            is_leaf: false,
            children: []
          }
        ],
        total: 1
      })

      router.push('/model-rules/1')
      await router.isReady()

      const wrapper = mount(ModelRules, {
        global: {
          plugins: [router]
        }
      })

      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      const ruleText = wrapper.find('.rule-text')
      expect(ruleText.exists()).toBe(true)
      expect(ruleText.text()).toBe(ruleWithNewlines)
      
      // 验证 white-space: pre-wrap 样式
      const styles = window.getComputedStyle(ruleText.element)
      expect(styles.whiteSpace).toBe('pre-wrap')
    })

    it('应该正确显示包含多个空格的规则内容', async () => {
      const ruleWithSpaces = '规则    内容    包含    多个空格'
      
      vi.mocked(modelApi.getModelVersion).mockResolvedValue({
        id: 1,
        version: 'v1.0',
        name: '测试版本',
        is_active: true
      })

      vi.mocked(modelApi.getModelNodes).mockResolvedValue({
        items: [
          {
            id: 1,
            code: 'TEST001',
            name: '测试节点',
            node_type: 'dimension',
            rule: ruleWithSpaces,
            is_leaf: true,
            children: []
          }
        ],
        total: 1
      })

      router.push('/model-rules/1')
      await router.isReady()

      const wrapper = mount(ModelRules, {
        global: {
          plugins: [router]
        }
      })

      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      const ruleText = wrapper.find('.rule-text')
      expect(ruleText.text()).toBe(ruleWithSpaces)
    })
  })

  describe('3. 空规则的显示', () => {
    it('应该显示"暂无规则说明"当规则为空字符串', async () => {
      vi.mocked(modelApi.getModelVersion).mockResolvedValue({
        id: 1,
        version: 'v1.0',
        name: '测试版本',
        is_active: true
      })

      vi.mocked(modelApi.getModelNodes).mockResolvedValue({
        items: [
          {
            id: 1,
            code: 'TEST001',
            name: '测试节点',
            node_type: 'sequence',
            rule: '',
            is_leaf: false,
            children: []
          }
        ],
        total: 1
      })

      router.push('/model-rules/1')
      await router.isReady()

      const wrapper = mount(ModelRules, {
        global: {
          plugins: [router]
        }
      })

      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      const ruleEmpty = wrapper.find('.rule-empty')
      expect(ruleEmpty.exists()).toBe(true)
      expect(ruleEmpty.text()).toBe('暂无规则说明')
    })

    it('应该显示"暂无规则说明"当规则为null', async () => {
      vi.mocked(modelApi.getModelVersion).mockResolvedValue({
        id: 1,
        version: 'v1.0',
        name: '测试版本',
        is_active: true
      })

      vi.mocked(modelApi.getModelNodes).mockResolvedValue({
        items: [
          {
            id: 1,
            code: 'TEST001',
            name: '测试节点',
            node_type: 'dimension',
            rule: null,
            is_leaf: false,
            children: []
          }
        ],
        total: 1
      })

      router.push('/model-rules/1')
      await router.isReady()

      const wrapper = mount(ModelRules, {
        global: {
          plugins: [router]
        }
      })

      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      const ruleEmpty = wrapper.find('.rule-empty')
      expect(ruleEmpty.exists()).toBe(true)
      expect(ruleEmpty.text()).toBe('暂无规则说明')
    })
  })

  describe('4. 树形结构的展开/收起', () => {
    it('应该默认展开所有节点', async () => {
      vi.mocked(modelApi.getModelVersion).mockResolvedValue({
        id: 1,
        version: 'v1.0',
        name: '测试版本',
        is_active: true
      })

      vi.mocked(modelApi.getModelNodes).mockResolvedValue({
        items: [
          {
            id: 1,
            code: 'PARENT',
            name: '父节点',
            node_type: 'sequence',
            rule: '父节点规则',
            is_leaf: false,
            children: [
              {
                id: 2,
                code: 'CHILD',
                name: '子节点',
                node_type: 'dimension',
                rule: '子节点规则',
                is_leaf: true,
                children: []
              }
            ]
          }
        ],
        total: 1
      })

      router.push('/model-rules/1')
      await router.isReady()

      const wrapper = mount(ModelRules, {
        global: {
          plugins: [router]
        }
      })

      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      const tree = wrapper.findComponent({ name: 'ElTree' })
      expect(tree.exists()).toBe(true)
      expect(tree.props('defaultExpandAll')).toBe(true)
    })
  })

  describe('5. 返回按钮功能', () => {
    it('应该显示返回按钮', async () => {
      vi.mocked(modelApi.getModelVersion).mockResolvedValue({
        id: 1,
        version: 'v1.0',
        name: '测试版本',
        is_active: true
      })

      vi.mocked(modelApi.getModelNodes).mockResolvedValue({
        items: [],
        total: 0
      })

      router.push('/model-rules/1')
      await router.isReady()

      const wrapper = mount(ModelRules, {
        global: {
          plugins: [router]
        }
      })

      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      const backButton = wrapper.find('.header-left button')
      expect(backButton.exists()).toBe(true)
      expect(backButton.text()).toContain('返回版本列表')
    })

    it('点击返回按钮应该导航回版本列表', async () => {
      vi.mocked(modelApi.getModelVersion).mockResolvedValue({
        id: 1,
        version: 'v1.0',
        name: '测试版本',
        is_active: true
      })

      vi.mocked(modelApi.getModelNodes).mockResolvedValue({
        items: [],
        total: 0
      })

      router.push('/model-rules/1')
      await router.isReady()

      const wrapper = mount(ModelRules, {
        global: {
          plugins: [router]
        }
      })

      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      const pushSpy = vi.spyOn(router, 'push')
      const backButton = wrapper.find('.header-left button')
      await backButton.trigger('click')

      expect(pushSpy).toHaveBeenCalledWith({ name: 'ModelVersions' })
    })
  })

  describe('6. 加载状态和错误处理', () => {
    it('应该在加载时显示loading状态', async () => {
      vi.mocked(modelApi.getModelVersion).mockImplementation(() => 
        new Promise(resolve => setTimeout(() => resolve({
          id: 1,
          version: 'v1.0',
          name: '测试版本',
          is_active: true
        }), 1000))
      )

      vi.mocked(modelApi.getModelNodes).mockImplementation(() =>
        new Promise(resolve => setTimeout(() => resolve({
          items: [],
          total: 0
        }), 1000))
      )

      router.push('/model-rules/1')
      await router.isReady()

      const wrapper = mount(ModelRules, {
        global: {
          plugins: [router]
        }
      })

      await wrapper.vm.$nextTick()

      const card = wrapper.findComponent({ name: 'ElCard' })
      expect(card.props('loading')).toBe(true)
    })

    it('应该处理无效的版本ID', async () => {
      router.push('/model-rules/invalid')
      await router.isReady()

      const wrapper = mount(ModelRules, {
        global: {
          plugins: [router]
        }
      })

      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      // 应该导航回版本列表
      expect(router.currentRoute.value.name).toBe('ModelVersions')
    })

    it('应该显示空状态当没有节点数据', async () => {
      vi.mocked(modelApi.getModelVersion).mockResolvedValue({
        id: 1,
        version: 'v1.0',
        name: '测试版本',
        is_active: true
      })

      vi.mocked(modelApi.getModelNodes).mockResolvedValue({
        items: [],
        total: 0
      })

      router.push('/model-rules/1')
      await router.isReady()

      const wrapper = mount(ModelRules, {
        global: {
          plugins: [router]
        }
      })

      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      const empty = wrapper.findComponent({ name: 'ElEmpty' })
      expect(empty.exists()).toBe(true)
      expect(empty.props('description')).toBe('暂无节点数据')
    })
  })

  describe('7. 节点信息显示', () => {
    it('应该正确显示节点类型标签', async () => {
      vi.mocked(modelApi.getModelVersion).mockResolvedValue({
        id: 1,
        version: 'v1.0',
        name: '测试版本',
        is_active: true
      })

      vi.mocked(modelApi.getModelNodes).mockResolvedValue({
        items: [
          {
            id: 1,
            code: 'SEQ001',
            name: '序列节点',
            node_type: 'sequence',
            rule: '规则内容',
            is_leaf: false,
            children: []
          },
          {
            id: 2,
            code: 'DIM001',
            name: '维度节点',
            node_type: 'dimension',
            rule: '规则内容',
            is_leaf: true,
            children: []
          }
        ],
        total: 2
      })

      router.push('/model-rules/1')
      await router.isReady()

      const wrapper = mount(ModelRules, {
        global: {
          plugins: [router]
        }
      })

      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      const tags = wrapper.findAllComponents({ name: 'ElTag' })
      expect(tags.length).toBeGreaterThan(0)
      
      const sequenceTag = tags.find(tag => tag.text() === '序列')
      expect(sequenceTag).toBeDefined()
      expect(sequenceTag?.props('type')).toBe('primary')

      const dimensionTag = tags.find(tag => tag.text() === '维度')
      expect(dimensionTag).toBeDefined()
      expect(dimensionTag?.props('type')).toBe('success')

      const leafTag = tags.find(tag => tag.text() === '末级')
      expect(leafTag).toBeDefined()
      expect(leafTag?.props('type')).toBe('warning')
    })
  })
})
