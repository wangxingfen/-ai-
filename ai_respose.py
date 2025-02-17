from openai import OpenAI

def ai_respose(message, messageses, config):
    client = OpenAI(
        api_key=config["api_key"],
        base_url=config["base_url"]
    )
    messages = [
        {'role': 'system', 'content': config["system_prompt"]},
        {'role': 'user', 'content': str(messageses) + message},
    ]
    completion = client.chat.completions.create(
        model=config.get("model", "deepseek-r1"),  # 使用配置中的模型
        messages=messages,
    )
    ai_respose = completion.choices[0].message.content
    context = []
    context.append({'role': 'user', 'content': message})
    context.append({'role': 'assistant', 'content': ai_respose})
    return ai_respose, context
