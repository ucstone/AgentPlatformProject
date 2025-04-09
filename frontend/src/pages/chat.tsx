export default function Chat() {
  return (
    <div className="container mx-auto py-10">
      <h1 className="text-4xl font-bold mb-8">智能客服</h1>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-card rounded-lg shadow-md p-6">
          <div className="h-[600px] flex flex-col">
            <div className="flex-1 overflow-y-auto mb-4">
              {/* 聊天消息列表将在这里显示 */}
            </div>
            <div className="flex gap-2">
              <input
                type="text"
                placeholder="输入您的问题..."
                className="flex-1 p-2 border rounded-md"
              />
              <button className="px-4 py-2 bg-primary text-white rounded-md">
                发送
              </button>
            </div>
          </div>
        </div>
        <div className="bg-card rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">会话历史</h2>
          <div className="space-y-2">
            {/* 会话历史列表将在这里显示 */}
          </div>
        </div>
      </div>
    </div>
  )
} 