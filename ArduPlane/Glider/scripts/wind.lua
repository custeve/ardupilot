

--[[
Wind schedule
--]]
local wind_sch = {
    {1457.7,314.2,3},
    {1515.4,314.3,3.8},
    {1554.1,319.7,4.2},
    {1612.4,317.1,4.2},
    {1661.3,319.9,4.4},
    {1740,322.5,5.2},
    {1819.3,326.4,6.2},
    {1909.2,327,7.3},
    {2000,329.1,8.6},
    {2101.9,327.7,9},
    {2215.1,328.3,9.9},
    {2361.2,327.5,10.3},
    {2509.4,325.9,10.5},
    {2649.1,325.5,11.3},
    {2845.9,323.8,11.8},
    {3035.4,315,11.9},
    {3228.8,295.9,13.7},
    {3473.1,280.9,17.6},
    {3723.7,272.6,22.8},
    {3993.6,267.6,25.3},
    {4284.2,263.7,26.6},
    {4623.8,264.1,26.8},
    {4962.5,267.2,26.7},
    {5314.1,271.1,26.8},
    {5724.6,273.4,26.7},
    {6123.1,273.1,26.6},
    {6556.6,271.6,28.7},
    {7012.3,269.8,33.5},
    {7493,270,38},
    {8002,271.1,39.4},
    {8522.6,271,40.9},
    {9055.5,271,42.7},
    {9625,270.9,42.1},
    {10211.9,270.3,39.3},
    {10817.8,272.4,37.1},
    {11444.5,271.7,35.4},
    {12061.9,270.4,36.1},
    {12734.2,271.6,36.5},
    {13396,271.6,33.2},
    {14124.3,268.1,28.4},
    {14840.9,274.7,26.6},
    {15535.2,288.8,25.6},
    {16303.1,310.5,18.5},
    {17079.4,275.3,14},
    {17872.8,313.2,16.7},
    {18687.7,304.5,5.4},
    {19540.9,119.8,0.2},
    {20424.8,289.9,5.7},
    {21377.7,298.4,7.3},
    {22385.1,272.2,7.9},
    {22908.2,271.7,10.7},
    {23451.1,272.7,13.4},
    {23992.3,271.2,17.5},
    {24576.8,275.5,19.9},
    {25156.4,274.7,20.4}
    
  }

local last_wind_alt = 0.0

function set_wind()
    local loc = ahrs:get_position()
    local alt = loc:alt() * 0.01
    local wind_alt = 0
    local target_speed = 20.0
    local target_dir = 270.0
    local num_rows = #wind_sch
    for row = 1, num_rows do
        if alt > wind_sch[row][1] then
            wind_alt = wind_sch[row][1]
            target_dir = wind_sch[row][2]
            target_speed = wind_sch[row][3]
        end
    end

    if wind_alt ~= last_wind_alt then
        gcs:send_text(0, string.format("Sim Wind Alt %.1f/%.1f %.1f/%.1f", alt, wind_alt, target_speed, target_dir))
        param:set('SIM_WIND_SPD', target_speed)
        param:set('SIM_WIND_DIR', target_dir)
        last_wind_alt = wind_alt
    end
    
end

function print_ahrs() 
    local velVar = ahrs:get_velocity_NED()
    --local wind = ahrs:wind_estimate()
    if velVar then 
        gcs:send_text(0, string.format("VEL %.1f,%.1f,%.1f", velVar:x(), velVar:y(), velVar:z()))
    end 
end

function update_wind()
    set_wind() 
    --print_ahrs()
    return update_wind,5000
end 



gcs:send_text(0, string.format("------Wind Loader-------- "))

return update_wind,10000