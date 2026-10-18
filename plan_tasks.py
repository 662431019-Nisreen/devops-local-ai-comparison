from crewai_helper import run_test
if __name__=='__main__':
    run_test('Plan remaining work','Create exactly 5 numbered steps in Thai. Each step needs an action and deliverable. Respect completed work: never propose repeating it. State missing information briefly. Do not add unrequested technologies.')
