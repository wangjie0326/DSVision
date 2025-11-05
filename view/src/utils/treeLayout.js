// utils/treeLayout.js - 树布局计算工具类

export class TreeLayoutEngine {
  constructor(nodeWidth = 60, nodeHeight = 60, levelHeight = 120, minSpacing = 80) {
    this.nodeWidth = nodeWidth;
    this.nodeHeight = nodeHeight;
    this.levelHeight = levelHeight;
    this.minSpacing = minSpacing;
  }

  /**
   * 递归计算子树所需的最小宽度
   * @param {Object} node - 树节点
   * @returns {number} 子树宽度
   */
  // utils/treeLayout.js - 只贴关键方法（替换你现有的方法）

  calculateSubtreeWidth(node) {
    if (!node) return 0;
    // 叶子节点只需要自身宽度
    if (!node.left && !node.right) return this.nodeWidth;

    const leftWidth = this.calculateSubtreeWidth(node.left);
    const rightWidth = this.calculateSubtreeWidth(node.right);

    // 如果两边都有子树，插入间距；否则 total 就是那一边的宽度
    let totalWidth = leftWidth + rightWidth;
    if (leftWidth > 0 && rightWidth > 0) totalWidth += this.minSpacing;

    return Math.max(totalWidth, this.nodeWidth);
  }


  /**
   * 递归布局树（后序遍历：先布局子树，再确定父节点位置）
   * 核心思想：父节点在两个子节点的垂直中分线上
   * @param {Object} node - 树节点
   * @param {number} centerX - 当前节点的中心X坐标
   * @param {number} y - 当前节点的Y坐标
   * @param {Object} positions - 存储所有节点位置的对象
   * @returns {Object} 所有节点的位置映射
   */
  layoutTree(node, centerX, y, positions = {}) {
    if (!node) return positions;
    const currentY = y;

    // 计算左右子树宽度（0 表示空）
    const leftWidth = this.calculateSubtreeWidth(node.left);
    const rightWidth = this.calculateSubtreeWidth(node.right);

    // 计算总占位宽度：左右宽 + 中间间距（只有两边都有时）
    let totalWidth = leftWidth + rightWidth;
    const hasBoth = leftWidth > 0 && rightWidth > 0;
    if (hasBoth) totalWidth += this.minSpacing;
    // 保证至少能容纳自身
    totalWidth = Math.max(totalWidth, this.nodeWidth);

    // leftStart 表示这棵子树（以当前 centerX 为中心）的最左边 x
    const leftStart = centerX - totalWidth / 2;

    // 根据 leftStart 分配左右子树的中心
    let leftCenter = null;
    let rightCenter = null;
    if (leftWidth > 0) {
      leftCenter = leftStart + leftWidth / 2;
    }
    if (rightWidth > 0) {
      // 右子树的起始 x = leftStart + leftWidth + (hasBoth ? minSpacing : 0)
      const rightStart = leftStart + leftWidth + (hasBoth ? this.minSpacing : 0);
      rightCenter = rightStart + rightWidth / 2;
    }

    // 先递归布局子节点（后序——先确定子节点位置）
    if (node.left) {
      this.layoutTree(node.left, leftCenter, y + this.levelHeight, positions);
    }
    if (node.right) {
      this.layoutTree(node.right, rightCenter, y + this.levelHeight, positions);
    }

    // 再确定当前父节点位置：如果有两个子节点取两子中心中点，
    // 否则在唯一子节点的基础上增加水平偏移，避免垂直重叠
    if (node.left && node.right) {
      const lx = positions[node.left.node_id].x;
      const rx = positions[node.right.node_id].x;
      positions[node.node_id] = { x: (lx + rx) / 2, y: currentY };
    } else if (node.left) {
      const leftX = positions[node.left.node_id].x;
      // 父节点稍微偏右
      positions[node.node_id] = { x: leftX + this.minSpacing / 2, y: currentY };
    } else if (node.right) {
      const rightX = positions[node.right.node_id].x;
      // 父节点稍微偏左
      positions[node.node_id] = { x: rightX - this.minSpacing / 2, y: currentY };
    } else {
      // 叶子节点
      positions[node.node_id] = { x: centerX, y: currentY };
    }


    return positions;
  }


  /**
   * 计算连接线路径（从父节点圆的边缘到子节点圆的边缘）
   * @param {Object} node - 树的根节点
   * @param {Object} positions - 节点位置映射
   * @returns {Array} 连接线数组
   */
  // calculateEdges：修复 path 的模板字符串并确保 id 用字符串
  calculateEdges(node, positions) {
    const edges = [];
    const radius = this.nodeHeight / 2;

    const traverse = (n) => {
      if (!n || !positions[n.node_id]) return;
      const parentPos = positions[n.node_id];

      const processChild = (child) => {
        if (!child || !positions[child.node_id]) return;
        const childPos = positions[child.node_id];
        const angle = Math.atan2(childPos.y - parentPos.y, childPos.x - parentPos.x);
        const startX = parentPos.x + radius * Math.cos(angle);
        const startY = parentPos.y + radius * Math.sin(angle);
        const endX = childPos.x - radius * Math.cos(angle);
        const endY = childPos.y - radius * Math.sin(angle);

        const cp1x = startX;
        const cp1y = startY + (endY - startY) * 0.3;
        const cp2x = endX;
        const cp2y = endY - (endY - startY) * 0.3;

        edges.push({
          id: `${n.node_id}-${child.node_id}`,
          // 用反引号构造 path 字符串
          path: `M ${startX} ${startY} C ${cp1x} ${cp1y}, ${cp2x} ${cp2y}, ${endX} ${endY}`,
          start: { x: startX, y: startY },
          end: { x: endX, y: endY }
        });
      };

      processChild(n.left);
      processChild(n.right);
      traverse(n.left);
      traverse(n.right);
    };

    traverse(node);
    return edges;
  }


  /**
   * 获取树的完整布局信息（节点位置 + 连接线）
   * @param {Object} root - 树的根节点
   * @param {number} startX - 起始X坐标（默认为画布中心）
   * @param {number} startY - 起始Y坐标（默认为80）
   * @returns {Object} { positions, edges, width, height }
   */
  getLayout(root, startX = null, startY = 80) {
    if (!root) {
      return { positions: {}, edges: [], width: 0, height: 0 };
    }

    // 计算总宽度
    const totalWidth = this.calculateSubtreeWidth(root);
    const canvasWidth = Math.max(totalWidth + 200, 1200);

    // 如果没有指定startX，使用画布中心
    const actualStartX = startX !== null ? startX : canvasWidth / 2;

    // 计算所有节点位置
    const positions = this.layoutTree(root, actualStartX, startY);

    // 计算所有连接线
    const edges = this.calculateEdges(root, positions);

    // 计算树的实际高度（找到最底层节点的Y坐标）
    const maxY = Math.max(...Object.values(positions).map(p => p.y));
    const height = maxY + this.nodeHeight + 50;

    return {
      positions,    // 节点位置映射
      edges,        // 连接线数组
      width: canvasWidth,
      height: height
    };
  }
}

// 导出默认实例
export default new TreeLayoutEngine();
