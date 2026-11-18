#include "pch.h"
#include "Shared/Emulator.h"
#include "Shared/EmuSettings.h"
#define private public
#include "NES/NesConsole.h"
#undef private
#include "NES/HdPacks/HdPackBuilder.h"
#include <filesystem>
#include <set>
#include "NES/HdPacks/HdNesPpu.h"
#include "Shared/NotificationManager.h"
#include "NES/HdPacks/HdPackLoader.h"
#include "NES/HdPacks/HdNesPack.h"
#include <unordered_set>
extern std::unique_ptr<Emulator> _emu;
extern "C" {
void InitDll();
void InitializeEmu(const char*,void*,void*,bool,bool,bool,bool);
bool LoadRom(const char*,const char*);
void Pause(); void Resume(); void Stop(); void Release();
void MoviePlay(const char*);
int LoadScript(const char*,const char*,const char*,int);
void GetScriptLog(int,char*,uint32_t);
void GetLog(char*,uint32_t);
}
#include "guarded_screen.h"
class CaptureListener : public INotificationListener {
public:
 int count=0;
 void ProcessNotification(ConsoleNotificationType type, void* param) override {
 if(type!=ConsoleNotificationType::PpuFrameDone) return;
 count++; if(count==1) std::cerr<<"Listener active"<<std::endl;
 int step=std::getenv("BIONIC_METADATA_STEP")?std::atoi(std::getenv("BIONIC_METADATA_STEP")):120; if(count%step!=0) return;
 auto nes=std::dynamic_pointer_cast<NesConsole>(_emu->GetConsole());
 auto ppu=dynamic_cast<HdNesPpu*>(nes->GetPpu()); if(!ppu)return;
 auto info=ppu->_info==ppu->_screenInfo[0]?ppu->_screenInfo[1]:ppu->_screenInfo[0];
 std::set<std::tuple<int,int,int,std::string,uint32_t,int,int>> entries;
 for(int y=0;y<240;y++) for(int x=0;x<256;x++){
 auto &px=info->ScreenTiles[y*256+x];
 auto add=[&](HdPpuTileInfo&t,int layer){if(t.TileIndex<0)return;int oy=t.OffsetY; if(layer && t.VerticalMirroring)oy=7-oy;std::string key; const char* hex="0123456789ABCDEF"; for(auto b:t.TileData){key+=hex[b>>4];key+=hex[b&15];} entries.insert({layer,x-t.OffsetX,y-oy,key,t.PaletteColors,t.HorizontalMirroring,t.VerticalMirroring});};
 if(!std::getenv("BIONIC_SPRITES_ONLY"))add(px.Tile,0);for(int k=0;k<px.SpriteCount;k++)add(px.Sprite[k],1);
 }
 const char* dir=std::getenv("BIONIC_METADATA_DIR"); if(!dir)return; char leaf[64];snprintf(leaf,sizeof(leaf),"%05d.tiles",count);std::ofstream out(std::filesystem::path(dir)/leaf);
 for(auto &e:entries){auto [l,x,y,t,p,h,v]=e;out<<l<<","<<x<<","<<y<<","<<t<<","<<p<<","<<h<<","<<v<<"\n";}
 }
};

class AuditPack : public BaseHdNesPack {
public:
 void Set(HdScreenInfo* p){_hdScreenInfo=p;}
 uint32_t GetScale()override{return 4;}
 void Process(HdScreenInfo*,uint32_t*,OverscanDimensions&)override{}
};
class AuditListener:public INotificationListener {
public:
 HdPackData data; AuditPack pack; int frame=0;
 std::unordered_map<HdPackTileInfo*,int> ids;
 struct Stat{int first=0,last=0,x=0,y=0;long count=0;};
 std::map<std::tuple<std::string,uint32_t,int,int>,Stat> stats;
 AuditListener(const std::string& file){if(!HdPackLoader::LoadHdNesPack(file,data))throw std::runtime_error("Audit pack load failed");int i=0;for(auto&t:data.Tiles)ids[t.get()]=i++;}
 void ProcessNotification(ConsoleNotificationType type,void*)override{
  if(type!=ConsoleNotificationType::PpuFrameDone)return;frame++;
  auto nes=std::dynamic_pointer_cast<NesConsole>(_emu->GetConsole());
  auto ppu=dynamic_cast<HdNesPpu*>(nes->GetPpu());if(!ppu)return;
  auto info=ppu->_info==ppu->_screenInfo[0]?ppu->_screenInfo[1]:ppu->_screenInfo[0];
  pack.Set(info);for(auto&c:data.Conditions)c->Initialize(info,&pack);
  std::unordered_set<uint64_t> seen;
  auto visit=[&](HdPpuTileInfo&t,int layer,int x,int y){
   if(t.TileIndex<0)return;
   int ox=x-(t.HorizontalMirroring?7-t.OffsetX:t.OffsetX);
   int oy=y-(t.VerticalMirroring?7-t.OffsetY:t.OffsetY);
   uint64_t h=((uint64_t)t.GetHashCode()<<32)|((uint64_t)layer<<20)|((uint64_t)(ox+8)<<10)|(oy+8);
   if(!seen.insert(h).second)return;
   int id=-1;auto it=data.TileByKey.find(t);
   if(it==data.TileByKey.end())it=data.TileByKey.find(t.GetKey(true));
   if(it!=data.TileByKey.end())for(auto *r:it->second)if(r->MatchesCondition(x,y,&t)){id=ids[r];break;}
   std::string key;const char*hex="0123456789ABCDEF";for(auto b:t.TileData){key+=hex[b>>4];key+=hex[b&15];}
   auto&st=stats[{key,t.PaletteColors,layer,id}];
   if(!st.first){st.first=frame;st.x=ox;st.y=oy;}st.last=frame;st.count++;
  };
  for(int y=8;y<232;y++)for(int x=0;x<256;x++){
   auto&px=info->ScreenTiles[y*256+x];
   // Background origins cover all cells, including clipped viewport edges.
   if((px.Tile.OffsetX==0||x==0)&&(px.Tile.OffsetY==0||y==8))visit(px.Tile,0,x,y);
   for(int k=0;k<px.SpriteCount;k++)visit(px.Sprite[k],1,x,y);
  }
 }
 void Save(const std::string&dir){
  std::ofstream f(dir+"/audit.tsv");f<<"key\tpalette\tlayer\trule\tfirst\tlast\tinstances\tx\ty\n";
  for(auto&[key,s]:stats){auto&[k,p,l,r]=key;f<<k<<"\t"<<std::hex<<std::uppercase<<p<<std::dec<<"\t"<<l<<"\t"<<r<<"\t"<<s.first<<"\t"<<s.last<<"\t"<<s.count<<"\t"<<s.x<<"\t"<<s.y<<"\n";}
  std::ofstream rules(dir+"/audit-rules.tsv");
  int n=0;for(auto&t:data.Tiles){rules<<n++<<"\t"<<t->ToString(0)<<"\n";}
 }
};
int main(int argc,char**argv){
 struct sigaction sa={};sa.sa_sigaction=fault;sa.sa_flags=SA_SIGINFO;sigaction(SIGSEGV,&sa,nullptr);
 if(argc<6) return 2;
 InitDll();
 InitializeEmu(argv[1],nullptr,nullptr,true,true,true,true);
 auto settings=_emu->GetSettings();
 auto &n=settings->GetNesConfig();
 n.Port1.Type=ControllerType::NesController;n.Port2.Type=ControllerType::NesController;
 n.EnableHdPacks=true;
 const uint32_t pal[64]={
 #include "palette.inc"
 };
 for(int i=0;i<512;i++) n.UserPalette[i]=pal[i%64];
 settings->GetDebugConfig().ScriptAllowIoOsAccess=true;
 settings->SetFlag(EmulationFlags::ConsoleMode);
 settings->SetFlag(EmulationFlags::MaximumSpeed);
 Pause();
 std::cerr<<"Loading ROM..."<<std::endl; if(!LoadRom(argv[2],"")) return 3; std::cerr<<"ROM loaded."<<std::endl;
 std::cerr<<"Loading movie..."<<std::endl; MoviePlay(argv[3]); std::cerr<<"Movie loaded."<<std::endl;
 auto nes=std::dynamic_pointer_cast<NesConsole>(_emu->GetConsole());
 std::cerr<<"PPU: "<<typeid(*nes->GetPpu()).name()<<" HD enabled: "<<n.EnableHdPacks<<std::endl;
 auto guardedPpu=dynamic_cast<HdNesPpu*>(nes->GetPpu());
 std::unique_ptr<GuardedScreen> guardA,guardB;
 if(guardedPpu){guardA=std::make_unique<GuardedScreen>(guardedPpu->_screenInfo[0]);guardB=std::make_unique<GuardedScreen>(guardedPpu->_screenInfo[1]);}
 bool build=std::string(argv[5])!="-";
 if(build){
 HdPackBuilderOptions opts={};opts.SaveFolder=argv[5];opts.FilterType=ScaleFilterType::Prescale;opts.Scale=1;opts.ChrRamBankSize=0x1000;opts.IgnoreOverscan=false;
 nes->StartRecordingHdPack(opts);
 }
 std::ifstream f(argv[4]);std::string script((std::istreambuf_iterator<char>(f)),{});
 int id=LoadScript("capture",argv[1],script.c_str(),-1);
 auto listener=std::make_shared<CaptureListener>();
 if(!build && !std::getenv("SKIP_METADATA")) _emu->GetNotificationManager()->RegisterNotificationListener(listener);
 std::shared_ptr<AuditListener> audit;
 if(const char* file=std::getenv("BIONIC_AUDIT_PACK")){audit=std::make_shared<AuditListener>(file);_emu->GetNotificationManager()->RegisterNotificationListener(audit);}
 settings->GetEmulationConfig().EmulationSpeed=0;
 settings->SetFlag(EmulationFlags::MaximumSpeed); Resume();
 for(int i=0;i<18000;i++){
 std::this_thread::sleep_for(std::chrono::milliseconds(100));
 if(std::filesystem::exists(std::string(argv[1])+"/done")) break;
 if(i%100==0){char log[16384]={};GetScriptLog(id,log,sizeof(log));std::cerr<<log<<std::endl;}
 }
 Pause();if(audit)audit->Save(argv[1]);if(build) nes->StopRecordingHdPack();
 char log[32768]={};GetLog(log,sizeof(log));std::cout<<log<<std::endl;
 GetScriptLog(id,log,sizeof(log));std::cout<<log<<std::endl;
 _emu->GetVideoDecoder()->WaitForAsyncFrameDecode();guardA.reset();guardB.reset();nes.reset();Stop();Release();return 0;
}
