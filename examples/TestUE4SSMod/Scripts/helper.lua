-- Test UE4SS Mod - Helper Functions
-- This file demonstrates how to organize code across multiple Lua files

local Helper = {}

-- Helper function to format messages
function Helper.FormatMessage(message, prefix)
    prefix = prefix or "[Test UE4SS Mod]"
    return string.format("%s %s", prefix, message)
end

-- Helper function to log with timestamp
function Helper.LogWithTime(message)
    local timestamp = os.date("%H:%M:%S")
    print(string.format("[%s] %s\n", timestamp, message))
end

-- Helper function to check if UE4SS is properly loaded
function Helper.CheckUE4SS()
    if ModRef then
        print(Helper.FormatMessage("UE4SS detected and working!\n"))
        return true
    else
        print("WARNING: UE4SS may not be properly initialized!\n")
        return false
    end
end

-- Initialize helper
Helper.CheckUE4SS()

return Helper
