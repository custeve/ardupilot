

--[[
Wind schedule for 11/15 from 11/9
--]]
local wind_sch = {
    {1496.14285718526,204.8,3},
    {1554.12524939006,204.9,3.6},
    {1592.96676175982,205.2,3.8},
    {1661.30300776436,203.9,3.9},
    {1710.40124185767,204.4,4.2},
    {1779.54565511952,199.1,4.5},
    {1859.15773006888,193,5.5},
    {1929.34294316779,188.9,6.5},
    {2030.47303314317,184,6.8},
    {2153.20311842889,180,7},
    {2267.05622087873,180,7.2},
    {2382.23578178463,185.3,7.5},
    {2541.50006022129,192.4,7.5},
    {2703.38953113997,200.9,7},
    {2879.07652256205,210.7,6.7},
    {3069.28229151409,223.6,6.3},
    {3286.37646662555,234.8,6.2},
    {3508.46904943888,244.1,5.8},
    {3760.07465570218,256.7,4.6},
    {4030.98301629228,270,3.4},
    {4322.74369803336,281.6,3.5},
    {4663.84722862094,280.1,4.2},
    {4990.18664841086,280.3,5.6},
    {5357.2276626205,276.6,7},
    {5739.59354064967,270,9.1},
    {6138.79251731814,268.6,11},
    {6573.04312873866,268.3,11.9},
    {7029.64470394457,269.1,13.3},
    {7529.70796347127,270,14.4},
    {8021.45098927461,268.5,14.7},
    {8543.27773943731,270.6,14.7},
    {9077.54035668674,273.9,14.1},
    {9648.65132169373,280.1,13.5},
    {10211.931499444,279.6,14},
    {10817.8012431894,281.2,14.4},
    {11444.4856113336,284.5,12.7},
    {12061.9388222539,277.4,13.8},
    {12734.1761196991,283.7,14.4},
    {13396.0397884817,282.4,17.8},
    {14124.2819827265,295.5,18.3},
    {14840.9336865429,293.9,17.5},
    {15535.173749959,296.1,17.3},
    {16303.0554374173,301.1,16.5},
    {17079.446135147,302.4,12.5},
    {17872.7691296227,298.2,12.5},
    {18687.681809928,295.4,12.6},
    {19540.923480394,297.5,14.2},
    {20436.3062411352,306.3,13.1},
    {21377.7069195228,282.8,10.3},
    {22385.0552371182,282.7,18.6},
    {22908.2416569715,286.9,20},
    {23451.0531328226,277.6,19.2},
    {23992.2799636203,261.9,21.5},
    {24576.750203255,261,24.9},
    {25156.4369293111,267.7,27.8}
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