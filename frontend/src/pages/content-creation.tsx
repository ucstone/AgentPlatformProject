export default function ContentCreation() {
  return (
    <div className="container mx-auto py-10">
      <h1 className="text-4xl font-bold mb-8">内容创作</h1>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-card rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">创作设置</h2>
          <div className="space-y-4">
            <div>
              <label className="block mb-2">内容类型</label>
              <select className="w-full p-2 border rounded-md">
                <option>文章</option>
                <option>广告文案</option>
                <option>社交媒体</option>
                <option>产品描述</option>
              </select>
            </div>
            <div>
              <label className="block mb-2">主题</label>
              <input
                type="text"
                className="w-full p-2 border rounded-md"
                placeholder="输入主题..."
              />
            </div>
            <div>
              <label className="block mb-2">关键词</label>
              <input
                type="text"
                className="w-full p-2 border rounded-md"
                placeholder="输入关键词，用逗号分隔..."
              />
            </div>
            <button className="w-full px-4 py-2 bg-primary text-white rounded-md">
              生成内容
            </button>
          </div>
        </div>
        <div className="bg-card rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">生成结果</h2>
          <div className="bg-muted p-4 rounded-md min-h-[400px]">
            {/* 生成的内容将在这里显示 */}
          </div>
        </div>
      </div>
    </div>
  )
} 