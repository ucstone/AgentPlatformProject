import React, { useState, useEffect } from 'react';
import { 
  getAvailableProviders, 
  getConfigs, 
  createConfig, 
  updateConfig, 
  deleteConfig,
  LLMConfigModel,
  LLMConfigCreateModel,
  ProvidersData
} from '../services/llm-config';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { toast } from '@/components/ui/use-toast';
import { PlusIcon, TrashIcon, Pencil1Icon } from '@radix-ui/react-icons';
import { Textarea } from "@/components/ui/textarea";

export default function ModelSettings() {
  const [configs, setConfigs] = useState<LLMConfigModel[]>([]);
  const [providers, setProviders] = useState<Record<string, string[]>>({});
  const [loading, setLoading] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [selectedConfig, setSelectedConfig] = useState<LLMConfigModel | null>(null);
  
  // 表单状态
  const [formData, setFormData] = useState<LLMConfigCreateModel>({
    name: '',
    provider: '',
    model_name: '',
    api_key: '',
    api_base_url: '',
    is_default: false
  });
  
  // 加载配置和提供商
  useEffect(() => {
    loadData();
  }, []);
  
  const loadData = async () => {
    setLoading(true);
    try {
      // 先获取提供商列表，再获取配置列表
      const providersRes = await getAvailableProviders();
      console.log("提供商响应:", providersRes);
      
      if (providersRes.data && providersRes.data.providers) {
        console.log("设置提供商数据:", providersRes.data.providers);
        setProviders(providersRes.data.providers);
      } else {
        console.error("提供商数据结构不正确:", providersRes);
        // 设置默认的提供商数据
        setProviders({
          "openai": ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"],
          "anthropic": ["claude-2", "claude-3-opus", "claude-3-sonnet"]
        });
      }
      
      const configsRes = await getConfigs();
      console.log("配置响应:", configsRes);
      
      if (configsRes.data && Array.isArray(configsRes.data)) {
        setConfigs(configsRes.data);
      } else {
        setConfigs([]);
      }
    } catch (error) {
      console.error("加载数据失败:", error);
      toast({
        title: "加载失败",
        description: "加载模型配置时发生错误",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };
  
  // 处理表单输入变化
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };
  
  // 处理选择变化
  const handleSelectChange = (name: string, value: string) => {
    if (name === 'provider') {
      // 当提供商变化时，重置模型名称并选择新提供商的第一个可用模型
      const models = providers[value] || [];
      const firstModel = models.length > 0 ? models[0] : '';
      
      setFormData(prev => ({ 
        ...prev, 
        [name]: value, 
        model_name: firstModel 
      }));
    } else {
      setFormData(prev => ({ ...prev, [name]: value }));
    }
  };
  
  // 处理默认开关变化
  const handleDefaultChange = (checked: boolean) => {
    setFormData(prev => ({ ...prev, is_default: checked }));
  };
  
  // 编辑配置
  const handleEdit = (config: LLMConfigModel) => {
    setSelectedConfig(config);
    
    // 验证provider和model存在性
    const providerExists = Object.keys(providers).includes(config.provider);
    const modelExists = providerExists && providers[config.provider]?.includes(config.model_name);
    
    setFormData({
      name: config.name,
      provider: providerExists ? config.provider : Object.keys(providers)[0] || '',
      model_name: modelExists ? config.model_name : 
                  (providerExists && providers[config.provider]?.length ? 
                    providers[config.provider][0] : ''),
      api_key: config.api_key || '',
      api_base_url: config.api_base_url || '',
      is_default: config.is_default
    });
    
    setIsEditing(true);
  };
  
  // 添加新配置
  const handleAddNew = () => {
    setSelectedConfig(null);
    
    // 确保providers有数据并且可以安全访问第一个键
    const providerKeys = Object.keys(providers);
    const defaultProvider = providerKeys.length > 0 ? providerKeys[0] : '';
    const defaultModels = defaultProvider ? providers[defaultProvider] || [] : [];
    const defaultModel = defaultModels.length > 0 ? defaultModels[0] : '';
    
    setFormData({
      name: '',
      provider: defaultProvider,
      model_name: defaultModel,
      api_key: '',
      api_base_url: '',
      is_default: false
    });
    
    setIsEditing(true);
  };
  
  // 取消编辑
  const handleCancel = () => {
    setIsEditing(false);
    setSelectedConfig(null);
  };
  
  // 保存配置
  const handleSave = async () => {
    try {
      let response;
      
      if (selectedConfig) {
        // 更新现有配置
        response = await updateConfig(selectedConfig.id, formData);
      } else {
        // 创建新配置
        response = await createConfig(formData);
      }
      
      if (response.data) {
        toast({
          title: selectedConfig ? '更新成功' : '创建成功',
          description: `模型配置「${formData.name}」已${selectedConfig ? '更新' : '创建'}`,
        });
        
        setIsEditing(false);
        setSelectedConfig(null);
        loadData();
      } else {
        toast({
          title: '操作失败',
          description: response.message || '未知错误',
          variant: 'destructive'
        });
      }
    } catch (error) {
      toast({
        title: '操作失败',
        description: '保存模型配置时发生错误',
        variant: 'destructive'
      });
    }
  };
  
  // 删除配置
  const handleDelete = async (config: LLMConfigModel) => {
    if (!window.confirm(`确定要删除配置「${config.name}」吗？`)) {
      return;
    }
    
    try {
      const response = await deleteConfig(config.id);
      
      // 204 No Content 或 success 为 true 都表示删除成功
      if (response.status === 204 || response.success) {
        toast({
          title: '删除成功',
          description: `模型配置「${config.name}」已删除`,
        });
        
        loadData();
      } else {
        toast({
          title: '删除失败',
          description: response.message || '未知错误',
          variant: 'destructive'
        });
      }
    } catch (error) {
      toast({
        title: '删除失败',
        description: '删除模型配置时发生错误',
        variant: 'destructive'
      });
    }
  };
  
  return (
    <div className="container mx-auto py-10 space-y-8">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">模型设置</h1>
        <Button onClick={handleAddNew} disabled={isEditing}>
          <PlusIcon className="mr-2 h-4 w-4" />
          添加配置
        </Button>
      </div>
      
      {isEditing ? (
        <Card>
          <CardHeader>
            <CardTitle>{selectedConfig ? '编辑配置' : '添加配置'}</CardTitle>
            <CardDescription>
              配置语言模型的提供商、API密钥和其他设置
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="name">配置名称</Label>
                <Input 
                  id="name"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  placeholder="例如：我的 GPT-4"
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="provider">提供商</Label>
                <Select 
                  value={formData.provider} 
                  onValueChange={(value: string) => handleSelectChange('provider', value)}
                >
                  <SelectTrigger id="provider" className="w-full">
                    <SelectValue placeholder="选择提供商" />
                  </SelectTrigger>
                  <SelectContent position="popper">
                    {Object.keys(providers).length > 0 ? (
                      Object.keys(providers).map((provider) => (
                        <SelectItem key={provider} value={provider}>
                          {provider}
                        </SelectItem>
                      ))
                    ) : (
                      <SelectItem value="no-providers" disabled>
                        暂无提供商数据
                      </SelectItem>
                    )}
                  </SelectContent>
                </Select>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="model_name">模型名称</Label>
                <Select 
                  value={formData.model_name} 
                  onValueChange={(value: string) => handleSelectChange('model_name', value)}
                  disabled={!formData.provider || !providers[formData.provider]}
                >
                  <SelectTrigger id="model_name" className="w-full">
                    <SelectValue placeholder="选择模型" />
                  </SelectTrigger>
                  <SelectContent position="popper">
                    {formData.provider && providers[formData.provider] ? (
                      providers[formData.provider].map((model) => (
                        <SelectItem key={model} value={model}>
                          {model}
                        </SelectItem>
                      ))
                    ) : (
                      <SelectItem value="no-models" disabled>
                        {!formData.provider ? "请先选择提供商" : "该提供商暂无模型数据"}
                      </SelectItem>
                    )}
                  </SelectContent>
                </Select>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="api_key">API密钥</Label>
                <Input 
                  id="api_key"
                  name="api_key"
                  value={formData.api_key}
                  onChange={handleInputChange}
                  placeholder="输入API密钥"
                  type="password"
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="api_base_url">API基础URL（可选）</Label>
                <Input 
                  id="api_base_url"
                  name="api_base_url"
                  value={formData.api_base_url}
                  onChange={handleInputChange}
                  placeholder="例如：https://api.openai.com/v1"
                />
              </div>
              
              <div className="flex items-center space-x-2 py-4">
                <Switch 
                  checked={formData.is_default}
                  onCheckedChange={handleDefaultChange}
                  id="is_default"
                />
                <Label htmlFor="is_default">设为默认配置</Label>
              </div>
            </div>
          </CardContent>
          <CardFooter className="flex justify-between">
            <Button variant="outline" onClick={handleCancel}>取消</Button>
            <Button onClick={handleSave}>保存</Button>
          </CardFooter>
        </Card>
      ) : (
        <Card>
          <CardHeader>
            <CardTitle>模型配置列表</CardTitle>
            <CardDescription>
              管理多个语言模型配置，设置默认模型。
            </CardDescription>
          </CardHeader>
          <CardContent>
            {configs.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                {loading ? '加载中...' : '暂无配置，请点击"添加配置"按钮创建'}
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>名称</TableHead>
                    <TableHead>提供商</TableHead>
                    <TableHead>模型</TableHead>
                    <TableHead>默认</TableHead>
                    <TableHead className="text-right">操作</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {configs.map((config) => (
                    <TableRow key={config.id}>
                      <TableCell className="font-medium">{config.name}</TableCell>
                      <TableCell>{config.provider}</TableCell>
                      <TableCell>{config.model_name}</TableCell>
                      <TableCell>
                        {config.is_default ? (
                          <span className="inline-flex items-center rounded-full bg-green-100 px-2.5 py-0.5 text-xs font-medium text-green-800">
                            默认
                          </span>
                        ) : null}
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-2">
                          <Button 
                            variant="ghost" 
                            size="sm"
                            onClick={() => handleEdit(config)}
                          >
                            <Pencil1Icon className="h-4 w-4" />
                          </Button>
                          <Button 
                            variant="ghost" 
                            size="sm"
                            onClick={() => handleDelete(config)}
                            disabled={config.is_default && configs.length > 1}
                          >
                            <TrashIcon className="h-4 w-4 text-red-500" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
} 