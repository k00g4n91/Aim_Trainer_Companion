import dearpygui.dearpygui as dpg

dpg.create_context()

width, height, channels, data = dpg.load_image("F:\coding\Bootcamp\10\scripts\pygui\Trackflix_logo.png")

with dpg.texture_registry():
    texture_id = dpg.add_static_texture(width, height, data)

with dpg.window(label="Tutorial"):
    dpg.add_image(texture_id)

dpg.start_dearpygui()

dpg.destroy_context()