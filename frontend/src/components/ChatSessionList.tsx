import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Session, deleteSession } from '../services/chat';
import { Loader2, Plus, Trash2 } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface ChatSessionListProps {
  sessions: Session[];
  currentSessionId?: string;
  loading: boolean;
  onCreateSession: () => Promise<void>;
  onDeleteSession: (id: string) => Promise<void>;
  onRefresh: () => Promise<void>;
}

const ChatSessionList: React.FC<ChatSessionListProps> = ({
  sessions,
  currentSessionId,
  loading,
  onCreateSession,
  onDeleteSession,
  onRefresh
}) => {
  const navigate = useNavigate();
  
  // 确保sessions是数组
  const sessionsList = Array.isArray(sessions) ? sessions : [];

  return (
    <div className="bg-card rounded-lg shadow-md p-6 h-full">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold">会话历史</h2>
        <div className="flex gap-2">
          <Button 
            variant="outline" 
            size="sm"
            onClick={onRefresh}
            disabled={loading}
          >
            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : "刷新"}
          </Button>
          <Button 
            variant="default" 
            size="sm"
            onClick={onCreateSession}
            disabled={loading}
          >
            <Plus className="h-4 w-4 mr-1" />
            新会话
          </Button>
        </div>
      </div>
      
      <div className="space-y-2 max-h-[550px] overflow-y-auto pr-1">
        {loading ? (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
          </div>
        ) : sessionsList.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            <p>暂无会话记录</p>
            <Button 
              variant="link" 
              onClick={onCreateSession}
              className="mt-2"
            >
              创建一个新会话
            </Button>
          </div>
        ) : (
          sessionsList.map((session) => (
            <div 
              key={session.id}
              className={`p-3 rounded-md cursor-pointer flex justify-between items-center transition-colors
                ${currentSessionId === session.id 
                  ? 'bg-primary/10 text-primary' 
                  : 'hover:bg-muted'}`}
              onClick={() => navigate(`/app/chat/${session.id}`)}
            >
              <div className="truncate flex-1 font-medium">
                {session.title || '未命名会话'}
                <div className="text-xs text-muted-foreground font-normal">
                  {new Date(session.created_at).toLocaleString()}
                </div>
              </div>
              <Button
                variant="ghost"
                size="icon"
                className="text-destructive ml-2 opacity-0 group-hover:opacity-100 hover:opacity-100"
                onClick={(e) => {
                  e.stopPropagation();
                  onDeleteSession(session.id);
                }}
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default ChatSessionList; 