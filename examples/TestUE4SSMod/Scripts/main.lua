-- Test UE4SS Mod - Main Script
-- Simple test to verify UE4SS is working properly in Brickadia

print("===========================================\n")
print("Test UE4SS Mod v1.0.0 Loaded Successfully!\n")
print("===========================================\n")

-- Initialize mod data
local ModRef = {}
ModRef.ModName = "TestUE4SSMod"
ModRef.ModVersion = "1.0.0"
ModRef.Author = "Brickadia Mod Loader"

print(string.format("[%s] Version: %s\n", ModRef.ModName, ModRef.ModVersion))
print(string.format("[%s] Author: %s\n", ModRef.ModName, ModRef.Author))
print(string.format("[%s] UE4SS Lua scripting is working!\n", ModRef.ModName))

-- Simple counter that increments
local counter = 0

-- Create a simple function
function ModRef.IncrementCounter()
    counter = counter + 1
    print(string.format("[%s] Counter incremented to: %d\n", ModRef.ModName, counter))
    return counter
end

-- Test the function
ModRef.IncrementCounter()
ModRef.IncrementCounter()
ModRef.IncrementCounter()

print(string.format("[%s] Test completed! Counter final value: %d\n", ModRef.ModName, counter))
print("[Test UE4SS Mod] Mod initialization complete!\n")
print("===========================================\n")
