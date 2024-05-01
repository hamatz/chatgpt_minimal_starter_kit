import inspect

class IntentConductor:
    def __init__(self):
        self.plugins = {}

    def register_plugin(self, plugin_name, plugin):
        self.plugins[plugin_name] = plugin

    def unregister_plugin(self, plugin_name):
        del self.plugins[plugin_name]

    def send_event(self, event_name, data, target_plugin=None):
        sender = self.get_sender()
        if target_plugin:
            plugin = self.plugins.get(target_plugin)
            if plugin:
                plugin.handle_event(event_name, data, sender=sender)
        else:
            for plugin_name, plugin in self.plugins.items():
                if plugin_name != sender:
                    plugin.handle_event(event_name, data, sender=sender)

    def get_sender(self):
        stack = inspect.stack()
        caller_frame = stack[2].frame
        caller_self = caller_frame.f_locals.get('self')
        sender = None
        for plugin_name, plugin in self.plugins.items():
            if plugin == caller_self:
                sender = plugin_name
                break
        return sender
    
    def register_task(self, task_id, task_definition, owner_plugin):
        self.tasks[task_id] = task_definition
        self.task_owners[task_id] = owner_plugin

    def execute_task(self, task_id, initial_data, caller_plugin):
        if task_id in self.tasks and self.task_owners[task_id] == caller_plugin:
            task_definition = self.tasks[task_id]
            self.send_event("task_start", {"task_id": task_id, "data": initial_data})
            for step in task_definition:
                self.send_event("task_step", {"task_id": task_id, "step": step})
            self.send_event("task_end", {"task_id": task_id})
        else:
            print(f"Warning: Unauthorized task execution attempt. Task ID: {task_id}, Caller: {caller_plugin}")