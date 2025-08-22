local was_changed = false

local function update()
    local loc = ahrs:get_position()

    if (arming:is_armed() and loc:alt() > 2500000) then
        param:set('SIM_SPEEDUP',1)
        gcs:send_text(0, "LUA: Changed sim speed to 1")
        was_changed = true
    end

end

local function loop()
    if was_changed then
        return loop, 500
    end
    update()
    return loop, 100
end

gcs:send_text(0, "LUA: Loaded sim speed changer")
return loop,1000