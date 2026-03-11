-- Standalone Path of Exile Character Importer (Non-interactive)

package.path = package.path .. ';../runtime/lua/?.lua'

local json = require("dkjson")

local realmList = {
	{ label = "PC", id = "PC", realmCode = "pc", hostName = "https://www.pathofexile.com/", profileURL = "account/view-profile/" },
	{ label = "Xbox", id = "XBOX", realmCode = "xbox", hostName = "https://www.pathofexile.com/", profileURL = "account/view-profile/" },
	{ label = "PS4", id = "SONY", realmCode = "sony", hostName = "https://www.pathofexile.com/", profileURL = "account/view-profile/" },
}

-- Function to download a URL
local function downloadPage(url, options)
	local tmpfile = os.tmpname()
	local command = "curl -s -L --max-time 15"
	if options and options.header then
		command = command .. " -H '" .. options.header .. "'"
	end
	command = command .. " -o " .. tmpfile .. " -w '%{http_code}' '" .. url .. "'"

	local f = io.popen(command)
	local http_code_str = f:read("*a")
	f:close()
	local http_code = tonumber(http_code_str)

	if http_code >= 400 then
		os.remove(tmpfile)
		return nil, "Response code: " .. http_code
	end

	local f_in = io.open(tmpfile, "r")
	if not f_in then
		os.remove(tmpfile)
		return nil, "Failed to open temporary file"
	end
	local response_body = f_in:read("*a")
	f_in:close()
	os.remove(tmpfile)

	return response_body, nil
end

-- Function to get character list
local function getCharacterList(realm, accountName, poesessid)
	local url = realm.hostName .. "character-window/get-characters?accountName=" .. accountName:gsub("#", "%%23") .. "&realm=" .. realm.realmCode
	local options = nil
	if poesessid then
		options = { header = "Cookie: POESESSID=" .. poesessid }
	end
	local body, err = downloadPage(url, options)
	if err then
		return nil, err
	end
	local success, data = pcall(json.decode, body)
	if not success then
		return nil, "Error decoding JSON"
	end
	return data, nil
end

-- Function to get passive tree
local function getPassiveTree(realm, accountName, characterName, poesessid)
	local url = realm.hostName .. "character-window/get-passive-skills?accountName=" .. accountName:gsub("#", "%%23") .. "&character=" .. characterName:gsub(" ", "%%20") .. "&realm=" .. realm.realmCode
	local options = nil
	if poesessid then
		options = { header = "Cookie: POESESSID=" .. poesessid }
	end
	local body, err = downloadPage(url, options)
	if err then
		return nil, err
	end
	return body, nil
end

-- Function to get items
local function getItems(realm, accountName, characterName, poesessid)
	local url = realm.hostName .. "character-window/get-items?accountName=" .. accountName:gsub("#", "%%23") .. "&character=" .. characterName:gsub(" ", "%%20") .. "&realm=" .. realm.realmCode
	local options = nil
	if poesessid then
		options = { header = "Cookie: POESESSID=" .. poesessid }
	end
	local body, err = downloadPage(url, options)
	if err then
		return nil, err
	end
	return body, nil
end

-- Main function
local function main()
	if #arg < 3 then
		print("Usage: lua import_character_cli.lua <realm> <account_name> <character_name> [poesessid]")
		print("Realms: PC, XBOX, SONY")
		print("Example: lua import_character_cli.lua SONY Ladimir_Lepin#9831 MiragMaraBatato")
		os.exit(1)
	end

	local realmId = arg[1]
	local accountName = arg[2]
	local characterName = arg[3]
	local poesessid = arg[4]

	local realm
	for _, r in ipairs(realmList) do
		if r.id == realmId then
			realm = r
			break
		end
	end

	if not realm then
		print("Invalid realm: " .. realmId)
		os.exit(1)
	end

	print("Downloading character list for " .. accountName)
	local charList, err = getCharacterList(realm, accountName, poesessid)
	if err then
		print("Error downloading character list: " .. err)
		os.exit(1)
	end

	-- Find character by name
	local selected_char = nil
	for _, char in ipairs(charList) do
		if char.name == characterName then
			selected_char = char
			break
		end
	end

	if not selected_char then
		print("Character not found: " .. characterName)
		print("Available characters:")
		for _, char in ipairs(charList) do
			print("  - " .. char.name .. " (Level " .. char.level .. ", " .. char.league .. ")")
		end
		os.exit(1)
	end

	print("Character found: " .. selected_char.name .. " (Level " .. selected_char.level .. ", " .. selected_char.league .. ")")

	print("Downloading passive tree for " .. selected_char.name .. "...")
	local passive_tree_json, err = getPassiveTree(realm, accountName, selected_char.name, poesessid)
	if err then
		print("Error downloading passive tree: " .. err)
		os.exit(1)
	end

	print("Downloading items for " .. selected_char.name .. "...")
	local items_json, err = getItems(realm, accountName, selected_char.name, poesessid)
	if err then
		print("Error downloading items: " .. err)
		os.exit(1)
	end

	local output = {
		character = selected_char,
		passive_tree = json.decode(passive_tree_json),
		items = json.decode(items_json),
	}

	local timestamp = os.date("%Y%m%d%H%M")
	local filename = selected_char.name .. "_" .. timestamp .. ".json"
	local f_out = io.open(filename, "w")
	if not f_out then
		print("Error creating output file.")
		os.exit(1)
	end
	f_out:write(json.encode(output))
	f_out:close()

	print("Character data saved to " .. filename)
end

main()
