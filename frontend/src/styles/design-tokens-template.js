/**
 * 设计规范模板
 * 从Figma Dev Mode提取设计规范后，填写到这里
 * 我会帮你创建完整的配置文件
 */

// ============================================
// 颜色系统 (Colors)
// ============================================
// 从Figma Dev Mode中提取颜色值，填写到下面
export const colors = {
  // 主色调
  primary: '#1890ff',        // ← 替换为你的主色调
  primaryHover: '#40a9ff',   // ← 主色调悬停状态
  primaryActive: '#096dd9',  // ← 主色调激活状态
  
  // 辅助色
  secondary: '#52c41a',      // ← 替换为你的辅助色
  
  // 状态色
  success: '#52c41a',         // ← 成功色
  warning: '#faad14',         // ← 警告色
  error: '#ff4d4f',          // ← 错误色
  info: '#1890ff',           // ← 信息色
  
  // 文字颜色
  textPrimary: '#000000',     // ← 主要文字颜色
  textSecondary: '#666666',  // ← 次要文字颜色
  textDisabled: '#bfbfbf',   // ← 禁用文字颜色
  
  // 背景色
  background: '#ffffff',      // ← 主背景色
  backgroundSecondary: '#f5f5f5', // ← 次要背景色
  
  // 边框色
  border: '#d9d9d9',         // ← 边框颜色
  borderLight: '#f0f0f0',    // ← 浅色边框
  
  // 其他
  divider: '#e8e8e8',        // ← 分割线颜色
}

// ============================================
// 字体系统 (Typography)
// ============================================
// 从Figma Dev Mode中提取字体信息，填写到下面
export const typography = {
  // 字体族
  fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
  
  // 字号和行高
  fontSize: {
    xs: '12px',    // ← 小字号
    sm: '14px',    // ← 较小字号
    base: '14px',  // ← 基础字号
    md: '16px',    // ← 中等字号
    lg: '18px',    // ← 较大字号
    xl: '20px',    // ← 大字号
    xxl: '24px',   // ← 超大字号
  },
  
  // 标题样式
  heading: {
    h1: {
      fontSize: '24px',      // ← H1字号
      fontWeight: 700,      // ← H1字重
      lineHeight: 1.2,      // ← H1行高
    },
    h2: {
      fontSize: '20px',     // ← H2字号
      fontWeight: 600,       // ← H2字重
      lineHeight: 1.3,      // ← H2行高
    },
    h3: {
      fontSize: '18px',     // ← H3字号
      fontWeight: 600,       // ← H3字重
      lineHeight: 1.4,      // ← H3行高
    },
    h4: {
      fontSize: '16px',     // ← H4字号
      fontWeight: 500,       // ← H4字重
      lineHeight: 1.4,      // ← H4行高
    },
  },
  
  // 正文字体
  body: {
    fontSize: '14px',       // ← 正文字号
    fontWeight: 400,        // ← 正文字重
    lineHeight: 1.5,        // ← 正文行高
  },
  
  // 小字体
  small: {
    fontSize: '12px',       // ← 小字号
    fontWeight: 400,        // ← 小字字重
    lineHeight: 1.4,        // ← 小字行高
  },
}

// ============================================
// 间距系统 (Spacing)
// ============================================
// 从Figma Dev Mode中提取间距值，填写到下面
export const spacing = {
  xs: '4px',    // ← 极小间距
  sm: '8px',    // ← 小间距
  md: '16px',   // ← 中等间距
  lg: '24px',   // ← 大间距
  xl: '32px',   // ← 超大间距
  xxl: '48px',  // ← 极大间距
}

// ============================================
// 圆角系统 (Border Radius)
// ============================================
export const borderRadius = {
  none: '0',
  sm: '2px',    // ← 小圆角
  md: '4px',    // ← 中等圆角
  lg: '8px',    // ← 大圆角
  xl: '12px',   // ← 超大圆角
  full: '9999px', // ← 完全圆形
}

// ============================================
// 阴影系统 (Shadows)
// ============================================
export const shadows = {
  sm: '0 1px 2px rgba(0, 0, 0, 0.05)',
  md: '0 4px 6px rgba(0, 0, 0, 0.1)',
  lg: '0 10px 15px rgba(0, 0, 0, 0.1)',
  xl: '0 20px 25px rgba(0, 0, 0, 0.1)',
}

// ============================================
// 布局系统 (Layout)
// ============================================
export const layout = {
  // 容器宽度
  containerMaxWidth: '1200px',
  
  // 侧边栏宽度
  sidebarWidth: '200px',
  
  // 头部高度
  headerHeight: '64px',
  
  // 内容区域内边距
  contentPadding: '24px',
}

// ============================================
// 组件样式 (Component Styles)
// ============================================
export const components = {
  // 按钮
  button: {
    height: {
      small: '24px',
      medium: '32px',
      large: '40px',
    },
    padding: {
      small: '0 8px',
      medium: '0 16px',
      large: '0 24px',
    },
    borderRadius: '4px',
  },
  
  // 输入框
  input: {
    height: '32px',
    padding: '4px 11px',
    borderRadius: '4px',
    borderWidth: '1px',
  },
  
  // 卡片
  card: {
    padding: '24px',
    borderRadius: '8px',
    boxShadow: shadows.md,
  },
}

// ============================================
// 导出所有设计规范
// ============================================
export default {
  colors,
  typography,
  spacing,
  borderRadius,
  shadows,
  layout,
  components,
}

