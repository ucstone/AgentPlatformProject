export default function Dashboard() {
  return (
    <div className="container mx-auto py-10">
      <h1 className="text-4xl font-bold mb-8">仪表盘</h1>
      <p className="text-lg text-muted-foreground">
        欢迎回来！您可以在这里快速访问平台的核心功能。
      </p>
      {/* 后续可以在这里添加更多仪表盘组件，如常用功能快捷入口、统计信息等 */}
      <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
         <div className="p-6 bg-card rounded-lg shadow-md border">
           <h2 className="text-xl font-semibold mb-3">快速开始</h2>
           <p className="text-muted-foreground">
             从左侧导航栏选择一个智能体开始探索吧！
           </p>
         </div>
         {/* 可以添加更多卡片 */}
      </div>
    </div>
  )
} 