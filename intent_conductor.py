class IntentConductor:
    def __init__(self, api):
        self.plugins = {}
        self.api = api

    def register_plugin(self, plugin_name, plugin):
        self.plugins[plugin_name] = plugin
        if hasattr(plugin, 'handle_event'):
            self.plugins[plugin_name].handle_event = plugin.handle_event.__get__(plugin)

    def unregister_plugin(self, plugin_name):
        del self.plugins[plugin_name]

    def send_event(self, event_name, data, sender_plugin, target_plugin=None):
        self.api.logger.info(f"Sending event: {event_name}, Data: {data}, Sender: {sender_plugin}, Target: {target_plugin}")
        if target_plugin:
            plugin = self.plugins.get(target_plugin)
            # 受け取り先プラグイン指定でのイベント送信はレスポンスを期待して呼び出されていると考えて結果をreurnする
            if plugin:
                return plugin.handle_event(event_name, data, sender_plugin)
        else:
            for plugin_name, plugin in self.plugins.items():
                if plugin_name != sender_plugin:
                    plugin.handle_event(event_name, data, sender_plugin)
            # ブロードキャストの場合はUIコンポーネントのテーマ変更など、受け取り側で処理をするだけでリプライ不要のメッセージと考えて処理終了後にただ"Finished"を返す
            return "Finished"
        
    def register_task(self, task_id, task_definition, owner_plugin_path):
        self.tasks[task_id] = task_definition
        self.task_owners[task_id] = owner_plugin_path

    def execute_task(self, task_id, initial_data, caller_plugin_path):
        if task_id in self.tasks and self.task_owners[task_id] == caller_plugin_path:
            task_definition = self.tasks[task_id]
            self.send_event("task_start", {"task_id": task_id, "data": initial_data})
            for step in task_definition:
                self.send_event("task_step", {"task_id": task_id, "step": step})
            self.send_event("task_end", {"task_id": task_id})
        else:
            self.api.logger.warning(f"Warning: Unauthorized task execution attempt. Task ID: {task_id}, Caller: {caller_plugin_path}")