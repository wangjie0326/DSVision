// utils/treeLayout.js - 树布局计算工具类（竖向、均匀、直线版）

export class TreeLayoutEngine {
  constructor(nodeWidth = 60, nodeHeight = 60, levelHeight = 120, minSpacing = 100) {
    this.nodeWidth = nodeWidth
    this.nodeHeight = nodeHeight
    this.levelHeight = levelHeight
    this.minSpacing = minSpacing
  }

  /** =========================
   * 计算子树宽度（递归）
   * ========================= */
  calculateSubtreeWidth(node) {
    if (!node) return 0
    if (!node.left && !node.right) return this.nodeWidth

    const leftWidth = this.calculateSubtreeWidth(node.left)
    const rightWidth = this.calculateSubtreeWidth(node.right)

    let total = leftWidth + rightWidth
    if (leftWidth > 0 && rightWidth > 0) total += this.minSpacing

    return Math.max(total, this.nodeWidth)
  }

  /** =========================
   * 核心布局算法（垂直树）
   * ========================= */
  layoutTree(node, centerX, y, positions = {}) {
    if (!node) return positions
    const currentY = y

    // 获取左右子树宽度
    const leftWidth = this.calculateSubtreeWidth(node.left)
    const rightWidth = this.calculateSubtreeWidth(node.right)
    const hasBoth = leftWidth > 0 && rightWidth > 0
    let totalWidth = leftWidth + rightWidth + (hasBoth ? this.minSpacing : 0)
    totalWidth = Math.max(totalWidth, this.nodeWidth)

    const leftStart = centerX - totalWidth / 2
    let leftCenter = null
    let rightCenter = null

    if (node.left) leftCenter = leftStart + leftWidth / 2
    if (node.right) {
      const rightStart = leftStart + leftWidth + (hasBoth ? this.minSpacing : 0)
      rightCenter = rightStart + rightWidth / 2
    }

    // ===== 递归布局子树 =====
    if (node.left) this.layoutTree(node.left, leftCenter, y + this.levelHeight, positions)
    if (node.right) this.layoutTree(node.right, rightCenter, y + this.levelHeight, positions)

    // ===== 父节点位置 =====
    if (node.left && node.right) {
      const lx = positions[node.left.node_id].x
      const rx = positions[node.right.node_id].x
      positions[node.node_id] = { x: (lx + rx) / 2, y: currentY }
    } else if (node.left) {
      const lx = positions[node.left.node_id].x
      positions[node.node_id] = { x: lx + this.minSpacing / 2, y: currentY }
    } else if (node.right) {
      const rx = positions[node.right.node_id].x
      positions[node.node_id] = { x: rx - this.minSpacing / 2, y: currentY }
    } else {
      positions[node.node_id] = { x: centerX, y: currentY }
    }

    return positions
  }

  /** =========================
   * 连线计算（直线 + 箭头）
   * ========================= */
  calculateEdges(node, positions) {
    const edges = []
    const radius = this.nodeHeight / 2

    const traverse = (n) => {
      if (!n || !positions[n.node_id]) return
      const parentPos = positions[n.node_id]

      const makeEdge = (child) => {
        if (!child || !positions[child.node_id]) return
        const childPos = positions[child.node_id]

        const dx = childPos.x - parentPos.x
        const dy = childPos.y - parentPos.y
        const distance = Math.sqrt(dx * dx + dy * dy)
        const ux = dx / distance
        const uy = dy / distance

        const startX = parentPos.x + radius * ux
        const startY = parentPos.y + radius * uy
        const endX = childPos.x - radius * ux
        const endY = childPos.y - radius * uy

        // 直线路径
        const path = `M ${startX} ${startY} L ${endX} ${endY}`

        edges.push({
          id: `${n.node_id}-${child.node_id}`,
          path,
          start: { x: startX, y: startY },
          end: { x: endX, y: endY }
        })
      }

      makeEdge(n.left)
      makeEdge(n.right)
      traverse(n.left)
      traverse(n.right)
    }

    traverse(node)
    return edges
  }

  /** =========================
   * 生成完整布局信息
   * ========================= */
  getLayout(root, startX = null, startY = 80) {
    if (!root) return { positions: {}, edges: [], width: 0, height: 0 }

    const totalWidth = this.calculateSubtreeWidth(root)
    const canvasWidth = Math.max(totalWidth + 200, 1200)
    const actualStartX = startX ?? canvasWidth / 2

    const positions = this.layoutTree(root, actualStartX, startY)
    const edges = this.calculateEdges(root, positions)
    const maxY = Math.max(...Object.values(positions).map(p => p.y))
    const height = maxY + this.nodeHeight + 100

    return {
      positions,
      edges,
      width: canvasWidth,
      height
    }
  }
}

export default new TreeLayoutEngine()

