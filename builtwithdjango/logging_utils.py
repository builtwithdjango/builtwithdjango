import logfire


def scrubbing_callback(m: logfire.ScrubMatch):
    if m.path == ("attributes", "cookies"):
        return m.value
