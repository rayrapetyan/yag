import acme.library.utils.pyrandr as randr

# get connected screens
cs = randr.connected_screens()[0]
reslist = cs.available_resolutions()
cs.set_resolution(tuple([int(x) for x in "640x480".split("x")]))
cs.apply_settings()
cs.set_resolution((1920, 1200))
cs.apply_settings()
