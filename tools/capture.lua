local out=assert(os.getenv('BIONIC_CAPTURE_DIR'))..'/'
local home=assert(os.getenv('BIONIC_CAPTURE_HOME'))
local last=tonumber(os.getenv('BIONIC_CAPTURE_FRAMES') or '40442')
local step=tonumber(os.getenv('BIONIC_CAPTURE_STEP') or '120')
local wanted_text=os.getenv('BIONIC_SCREENSHOT_FRAMES')
local wanted={}
if wanted_text then for f in string.gmatch(wanted_text,'%d+') do wanted[tonumber(f)]=true end end
local n=0
local function save(path,data) local f=assert(io.open(path,'wb'));f:write(data);f:close() end
local function mem(t,size)
 local a={};for i=0,size-1 do a[#a+1]=string.char(emu.read(i,t)) end;return table.concat(a)
end
local function frame()
 n=n+1
 local checkpoint=n%step==0 or n==1 or n==last
 if (wanted_text and wanted[n]) or (not wanted_text and checkpoint) then
  save(out..string.format('%05d.png',n),emu.takeScreenshot())
 end
 if checkpoint then
  save(out..string.format('%05d.ram',n),mem(emu.memType.nesInternalRam,2048))
  save(out..string.format('%05d.ppu',n),mem(emu.memType.nesPpuMemory,0x4000))
  if n%1200==0 then emu.log('Frame '..n..' / '..last) end
 end
 if n==last then save(home..'/done',tostring(n));emu.breakExecution() end
end
emu.addEventCallback(frame,emu.eventType.endFrame)
