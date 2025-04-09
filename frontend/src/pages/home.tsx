export default function Home() {
  return (
    <div className="container mx-auto py-10">
      <h1 className="text-4xl font-bold mb-8">欢迎使用智能体综合应用平台</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="p-6 bg-card rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4">智能客服</h2>
          <p className="text-muted-foreground">
            提供智能化的客户服务支持，24/7 全天候响应客户需求。
          </p>
        </div>
        <div className="p-6 bg-card rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4">Text2SQL</h2>
          <p className="text-muted-foreground">
            通过自然语言生成 SQL 查询，轻松进行数据分析。
          </p>
        </div>
        <div className="p-6 bg-card rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4">知识库</h2>
          <p className="text-muted-foreground">
            智能化的企业知识管理，快速获取所需信息。
          </p>
        </div>
        <div className="p-6 bg-card rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4">文案创作</h2>
          <p className="text-muted-foreground">
            智能生成各类文案内容，提高创作效率。
          </p>
        </div>
      </div>
    </div>
  )
} 