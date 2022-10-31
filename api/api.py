import main

def application(env, start_response):
    return main.run(env,start_response)
