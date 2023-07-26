import solara.lab

disabled = solara.reactive(False)
icon = solara.reactive(True)

def tab():
    with solara.lab.Tab("1. Select Engine"):
        with solara.lab.Tabs():
                with solara.lab.Tab("FSM Files"):
                    solara.Checkbox(label="Disable Tab 2", value=disabled)
                    solara.Checkbox(label="Show icon", value=icon)
                    solara.Markdown("Hello")
                with solara.lab.Tab("Start Analysis from Installed Fleet"):
                    solara.Checkbox(label="Disable Tab 2", value=disabled)
                    solara.Checkbox(label="Show icon", value=icon)
                    solara.Markdown("Hello")