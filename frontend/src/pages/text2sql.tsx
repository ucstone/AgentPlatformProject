export default function Text2SQL() {
  return (
    <div className="container mx-auto py-10">
      <h1 className="text-4xl font-bold mb-8">Text2SQL</h1>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-card rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">自然语言查询</h2>
          <textarea
            className="w-full h-32 p-2 border rounded-md mb-4"
            placeholder="输入您的查询问题..."
          />
          <button className="px-4 py-2 bg-primary text-white rounded-md">
            生成 SQL
          </button>
        </div>
        <div className="bg-card rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">生成的 SQL</h2>
          <div className="bg-muted p-4 rounded-md font-mono">
            {/* SQL 查询结果将在这里显示 */}
          </div>
        </div>
      </div>
    </div>
  )
} 