#pragma once
#include <sys/mman.h>
#include <unistd.h>
#include <signal.h>
#include <execinfo.h>
#include "Shared/Video/VideoDecoder.h"
struct GuardedScreen {
 HdScreenInfo* screen; HdPpuPixelInfo* original; void* memory; size_t bytes,page;
 GuardedScreen(HdScreenInfo* s):screen(s),original(s->ScreenTiles) {
  bytes=sizeof(HdPpuPixelInfo)*NesConstants::ScreenPixelCount;page=sysconf(_SC_PAGESIZE);
  if(bytes%page)throw std::runtime_error("screen size not aligned");
  memory=mmap(nullptr,bytes+page,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS,-1,0);
  if(memory==MAP_FAILED)throw std::runtime_error("mmap failed");
  memcpy(memory,original,bytes);mprotect((char*)memory+bytes,page,PROT_NONE);screen->ScreenTiles=(HdPpuPixelInfo*)memory;
  std::cerr<<"Screen guard begins at "<<(void*)((char*)memory+bytes)<<std::endl;
 }
 ~GuardedScreen(){memcpy(original,memory,bytes);screen->ScreenTiles=original;munmap(memory,bytes+page);}
};
void fault(int sig,siginfo_t* info,void*){char text[160];int n=snprintf(text,sizeof(text),"Guarded playback fault signal %d at %p\n",sig,info->si_addr);write(2,text,n);void* bt[40];int k=backtrace(bt,40);backtrace_symbols_fd(bt,k,2);_exit(128+sig);}
