// Capture the completed decoded frame, avoiding screenshots racing the video thread.
#define private public
#include "Shared/Video/VideoDecoder.h"
#undef private
#include "Shared/Video/BaseVideoFilter.h"
extern "C" unsigned long long XXH3_64bits(const void*,size_t);
class SyncCaptureListener:public INotificationListener {
 int frame=0;std::set<int>wanted;std::ofstream hashes;std::string dir;
 void Wait(){auto*d=_emu->GetVideoDecoder();while(d->_frameChanged.load())std::this_thread::yield();}
 void Hash(int n){auto*d=_emu->GetVideoDecoder();if(!d->_videoFilter)return;auto sz=d->GetFrameInfo();auto*b=d->_videoFilter->GetOutputBuffer();if(b&&sz.Width&&sz.Height)hashes<<n<<"\t"<<std::hex<<XXH3_64bits(b,(size_t)sz.Width*sz.Height*4)<<std::dec<<"\n";}
 public:
 SyncCaptureListener(){
  dir=std::getenv("BIONIC_CAPTURE_DIR");const char* w=std::getenv("BIONIC_SCREENSHOT_FRAMES");if(w){std::stringstream s(w);std::string v;while(std::getline(s,v,','))wanted.insert(std::stoi(v));}
  if(std::getenv("BIONIC_HASH_FRAMES"))hashes.open(std::string(std::getenv("BIONIC_CAPTURE_HOME"))+"/rendered-hashes.tsv");
 }
 void ProcessNotification(ConsoleNotificationType t,void*)override{
  if(t!=ConsoleNotificationType::PpuFrameDone)return;++frame;
  if(hashes.is_open()||wanted.count(frame))Wait();
  if(hashes.is_open()&&frame>1)Hash(frame-1);
  if(wanted.count(frame)&&frame>1){std::stringstream ss;_emu->GetVideoDecoder()->TakeScreenshot(ss);char leaf[64];snprintf(leaf,sizeof(leaf),"/%05d.png",frame);std::ofstream f(dir+leaf,std::ios::binary);f<<ss.rdbuf();}
 }
 void Finish(){Wait();if(hashes.is_open()){Hash(frame);hashes.flush();}}
};
