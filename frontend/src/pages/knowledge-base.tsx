export default function KnowledgeBase() {
  return (
    <div className="container mx-auto py-10">
      <h1 className="text-4xl font-bold mb-8">知识库</h1>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-card rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">知识库问答</h2>
          <div className="space-y-4">
            <input
              type="text"
              placeholder="输入您的问题..."
              className="w-full p-2 border rounded-md"
            />
            <div className="bg-muted p-4 rounded-md min-h-[200px]">
              {/* 问答结果将在这里显示 */}
            </div>
          </div>
        </div>
        <div className="bg-card rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">知识库管理</h2>
          <div className="space-y-4">
            <button className="w-full px-4 py-2 bg-primary text-white rounded-md">
              上传文档
            </button>
            <div className="space-y-2">
              {/* 文档列表将在这里显示 */}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
} 