#define _DARWIN_C_SOURCE 1
#include <errno.h>
#include <fcntl.h>
#include <grp.h>
#include <libgen.h>
#include <pwd.h>
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>

extern char **environ;

#ifndef AUTHORITY_ROOT
#define AUTHORITY_ROOT "/Library/Application Support/Nortropic/provenance"
#endif
#ifndef PROBE_SHA256
#error PROBE_SHA256 must bind the exact probe artifact
#endif
#ifndef ALLOWLIST_SHA256
#error ALLOWLIST_SHA256 must bind the exact protected allowlist
#endif

#define DOC_MAX 8192
#define ARTIFACT_MAX (1024 * 1024)
#define PATH_MAX_LOCAL 1024

typedef struct {
  const char *request_id;
  const char *candidate;
  const char *spec;
  const char *gate;
  const char *probe;
  const char *result;
  const char *marker;
} Request;

typedef struct { uint32_t h[8]; uint64_t bits; unsigned char block[64]; size_t used; } Sha256;
static uint32_t rr(uint32_t x,unsigned n){return (x>>n)|(x<<(32-n));}
static void sha_block(Sha256 *s,const unsigned char *b){
  static const uint32_t k[64]={
    0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,
    0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,
    0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,
    0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,
    0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,
    0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
    0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,
    0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2};
  uint32_t w[64];
  for(int i=0;i<16;i++)w[i]=(uint32_t)b[4*i]<<24|(uint32_t)b[4*i+1]<<16|(uint32_t)b[4*i+2]<<8|b[4*i+3];
  for(int i=16;i<64;i++){uint32_t x=w[i-15],y=w[i-2];w[i]=w[i-16]+(rr(x,7)^rr(x,18)^(x>>3))+w[i-7]+(rr(y,17)^rr(y,19)^(y>>10));}
  uint32_t a=s->h[0],bb=s->h[1],c=s->h[2],d=s->h[3],e=s->h[4],f=s->h[5],g=s->h[6],h=s->h[7];
  for(int i=0;i<64;i++){uint32_t s1=rr(e,6)^rr(e,11)^rr(e,25),ch=(e&f)^((~e)&g),t1=h+s1+ch+k[i]+w[i],s0=rr(a,2)^rr(a,13)^rr(a,22),maj=(a&bb)^(a&c)^(bb&c),t2=s0+maj;h=g;g=f;f=e;e=d+t1;d=c;c=bb;bb=a;a=t1+t2;}
  s->h[0]+=a;s->h[1]+=bb;s->h[2]+=c;s->h[3]+=d;s->h[4]+=e;s->h[5]+=f;s->h[6]+=g;s->h[7]+=h;
}
static void sha_init(Sha256*s){uint32_t h[8]={0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19};memcpy(s->h,h,sizeof h);s->bits=0;s->used=0;}
static void sha_add(Sha256*s,const unsigned char*p,size_t n){s->bits+=(uint64_t)n*8;while(n){size_t take=64-s->used;if(take>n)take=n;memcpy(s->block+s->used,p,take);s->used+=take;p+=take;n-=take;if(s->used==64){sha_block(s,s->block);s->used=0;}}}
static void sha_final(Sha256*s,char out[65]){s->block[s->used++]=0x80;if(s->used>56){while(s->used<64)s->block[s->used++]=0;sha_block(s,s->block);s->used=0;}while(s->used<56)s->block[s->used++]=0;for(int i=7;i>=0;i--)s->block[s->used++]=(unsigned char)(s->bits>>(8*i));sha_block(s,s->block);for(int i=0;i<8;i++)sprintf(out+8*i,"%08x",s->h[i]);out[64]=0;}
static void digest(const unsigned char*p,size_t n,char out[65]){Sha256 s;sha_init(&s);sha_add(&s,p,n);sha_final(&s,out);}

static int protected_mode(mode_t mode) { return (mode & 0022) == 0; }
static int regular(const struct stat *s, uid_t owner) {
  return S_ISREG(s->st_mode) && s->st_uid == owner && protected_mode(s->st_mode) && s->st_nlink == 1;
}
static int directory(const struct stat *s, uid_t owner) {
  return S_ISDIR(s->st_mode) && s->st_uid == owner && protected_mode(s->st_mode);
}
static int same_stat(const struct stat *a,const struct stat *b){
  return a->st_dev==b->st_dev&&a->st_ino==b->st_ino&&a->st_mode==b->st_mode&&a->st_uid==b->st_uid&&
    a->st_gid==b->st_gid&&a->st_nlink==b->st_nlink&&a->st_size==b->st_size&&
    a->st_mtimespec.tv_sec==b->st_mtimespec.tv_sec&&a->st_mtimespec.tv_nsec==b->st_mtimespec.tv_nsec&&
    a->st_ctimespec.tv_sec==b->st_ctimespec.tv_sec&&a->st_ctimespec.tv_nsec==b->st_ctimespec.tv_nsec;
}
static int lower_hex(const char *s,size_t n){for(size_t i=0;i<n;i++)if(!((s[i]>='0'&&s[i]<='9')||(s[i]>='a'&&s[i]<='f')))return 0;return s[n]==0;}
static int valid_atom(const char *s,size_t max){size_t n=strlen(s);if(n==0||n>max)return 0;for(size_t i=0;i<n;i++)if((unsigned char)s[i]<0x21||(unsigned char)s[i]>0x7e||s[i]=='"'||s[i]=='\\')return 0;return 1;}
static uid_t authority_uid(void) {
#ifdef NORTROPIC_FIXTURE
  return geteuid();
#else
  return 0;
#endif
}
static int producer_ids(uid_t *uid,gid_t *gid){
#ifdef NORTROPIC_FIXTURE
  *uid=getuid();*gid=getgid();return 1;
#else
  struct passwd *p=getpwnam("_nortropic_provenance");
  if(!p||p->pw_uid==0||p->pw_uid==getuid())return 0;
  *uid=p->pw_uid;*gid=p->pw_gid;return 1;
#endif
}
static int drop_identity(uid_t uid,gid_t gid){
#ifdef NORTROPIC_FIXTURE
  return uid==getuid()&&gid==getgid();
#else
  return setgroups(1,&gid)==0&&setgid(gid)==0&&setuid(uid)==0;
#endif
}
static int root_fd(void){
#ifdef NORTROPIC_FIXTURE
  int fd=open(AUTHORITY_ROOT,O_RDONLY|O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC);struct stat s;
  if(fd<0||fstat(fd,&s)||!directory(&s,authority_uid())){if(fd>=0)close(fd);return -1;}return fd;
#else
  const char *parts[]={"Library","Application Support","Nortropic","provenance"};
  int fd=open("/",O_RDONLY|O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC);struct stat s;
  if(fd<0||fstat(fd,&s)||!directory(&s,0)){if(fd>=0)close(fd);return -1;}
  for(size_t i=0;i<4;i++){int next=openat(fd,parts[i],O_RDONLY|O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC);close(fd);fd=next;if(fd<0||fstat(fd,&s)||!directory(&s,0)){if(fd>=0)close(fd);return -1;}}
  return fd;
#endif
}
static int child_dir(int parent,const char *name,uid_t owner){int fd=openat(parent,name,O_RDONLY|O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC);struct stat s;if(fd<0||fstat(fd,&s)||!directory(&s,owner)){if(fd>=0)close(fd);return -1;}return fd;}
static int read_stable(int dir,const char *name,uid_t owner,unsigned char *out,size_t cap,size_t *n){
  int fd=openat(dir,name,O_RDONLY|O_NOFOLLOW|O_CLOEXEC);struct stat a,b,c;if(fd<0)return 0;
  if(fstat(fd,&a)||!regular(&a,owner)||a.st_size<=0||(size_t)a.st_size>=cap){close(fd);return 0;}
  ssize_t x=pread(fd,out,(size_t)a.st_size,0);if(x!=a.st_size||fstat(fd,&b)){close(fd);return 0;}
  unsigned char second[DOC_MAX];ssize_t y=pread(fd,second,(size_t)a.st_size,0);if(y!=a.st_size||memcmp(out,second,(size_t)a.st_size)||fstat(fd,&c)||!same_stat(&a,&b)||!same_stat(&b,&c)){close(fd);return 0;}
  close(fd);*n=(size_t)a.st_size;return 1;
}
static int exact_allowlist(void){
  int root=root_fd();if(root<0)return 0;unsigned char raw[DOC_MAX];size_t n=0;char sum[65];int ok=read_stable(root,"probes.json",authority_uid(),raw,sizeof raw,&n);close(root);if(!ok)return 0;digest(raw,n,sum);return strcmp(sum,ALLOWLIST_SHA256)==0;
}
static int write_exact(int dir,const char *name,const unsigned char *raw,size_t n,mode_t mode){
  int fd=openat(dir,name,O_WRONLY|O_CREAT|O_EXCL|O_NOFOLLOW|O_CLOEXEC,mode);if(fd<0)return 0;
  size_t done=0;while(done<n){ssize_t q=write(fd,raw+done,n-done);if(q<=0){close(fd);unlinkat(dir,name,0);return 0;}done+=(size_t)q;}
  int ok=fsync(fd)==0&&fchmod(fd,mode)==0;close(fd);if(!ok)unlinkat(dir,name,0);return ok;
}

static int request_args(int argc,char **argv,int kind,Request *r,char generated[65]){
  static const char *keys[]={"--request-id","--task","--candidate","--task-spec-sha256","--gate-sha256","--probe"};
  int off=kind==2?2:1;
  if(kind==0){
    static const char *producer_keys[]={"--task","--candidate","--task-spec-sha256","--gate-sha256","--probe"};
    if(argc!=11)return 0;for(int i=0;i<5;i++)if(strcmp(argv[1+2*i],producer_keys[i]))return 0;
    if(strcmp(argv[2],"h-033"))return 0;
    unsigned char random_bytes[32];arc4random_buf(random_bytes,sizeof random_bytes);
    for(size_t i=0;i<sizeof random_bytes;i++)sprintf(generated+2*i,"%02x",random_bytes[i]);generated[64]=0;
    r->request_id=generated;r->candidate=argv[4];r->spec=argv[6];r->gate=argv[8];r->probe=argv[10];
  } else {
    if((kind==2&&(argc!=16||strcmp(argv[1],"consume")))||(kind==1&&argc!=13))return 0;
    for(int i=0;i<6;i++)if(strcmp(argv[off+2*i],keys[i]))return 0;
    if(strcmp(argv[off+3],"h-033"))return 0;
    r->request_id=argv[off+1];r->candidate=argv[off+5];r->spec=argv[off+7];r->gate=argv[off+9];r->probe=argv[off+11];
  }
  if(!lower_hex(r->request_id,64)||!lower_hex(r->candidate,40)||!lower_hex(r->spec,64)||!lower_hex(r->gate,64))return 0;
  if(strcmp(r->probe,"h033-auth-pass-v1")==0){r->result="PASS";r->marker="h033-effect-pass-v1";}
  else if(strcmp(r->probe,"h033-auth-fail-v1")==0){r->result="FAIL";r->marker="h033-effect-fail-v1";}
  else if(strcmp(r->probe,"h033-auth-odombart-v1")==0){r->result="ODÖMBART";r->marker="h033-effect-odombart-v1";}
  else return 0;
  if(kind==2){if(strcmp(argv[14],"--require-result")||strcmp(argv[15],r->result))return 0;}
  return valid_atom(r->probe,64);
}
static int receipt_json(const Request*r,char*out,size_t cap){char path[PATH_MAX_LOCAL];int p=snprintf(path,sizeof path,"%s/probes/%s",AUTHORITY_ROOT,r->probe);if(p<0||(size_t)p>=sizeof path)return -1;return snprintf(out,cap,"{\"schema_version\":1,\"observer_authority\":\"root-owned-h033-observer-v1\",\"request_id\":\"%s\",\"candidate_sha\":\"%s\",\"probe_identity\":\"%s\",\"probe_path\":\"%s\",\"probe_sha256\":\"%s\",\"effect_marker\":\"%s\"}\n",r->request_id,r->candidate,r->probe,path,PROBE_SHA256,r->marker);}
static int evidence_json(const Request*r,const char *effect,char*out,size_t cap){return snprintf(out,cap,"{\"schema_version\":1,\"producer_authority\":\"_nortropic_provenance\",\"task\":\"h-033\",\"candidate_sha\":\"%s\",\"task_spec_sha256\":\"%s\",\"gate_sha256\":\"%s\",\"probe_identity\":\"%s\",\"request_id\":\"%s\",\"result\":\"%s\",\"effect_sha256\":\"%s\"}\n",r->candidate,r->spec,r->gate,r->probe,r->request_id,r->result,effect);}
static int token_json(const Request*r,char*out,size_t cap){return snprintf(out,cap,"{\"schema_version\":1,\"request_id\":\"%s\",\"task\":\"h-033\",\"candidate_sha\":\"%s\",\"task_spec_sha256\":\"%s\",\"gate_sha256\":\"%s\",\"probe_identity\":\"%s\",\"result\":\"%s\"}\n",r->request_id,r->candidate,r->spec,r->gate,r->probe,r->result);}

static int run_probe(const Request*r,uid_t uid,gid_t gid){
  int root=root_fd(),probes=root<0?-1:child_dir(root,"probes",authority_uid());if(root>=0)close(root);if(probes<0)return 0;
  int fd=openat(probes,r->probe,O_RDONLY|O_NOFOLLOW|O_CLOEXEC);struct stat before,after,current;unsigned char raw[ARTIFACT_MAX];char sum[65],path[PATH_MAX_LOCAL];
  if(fd<0||fstat(fd,&before)||!regular(&before,authority_uid())||!(before.st_mode&0111)||before.st_size<=0||before.st_size>=ARTIFACT_MAX){if(fd>=0)close(fd);close(probes);return 0;}
  ssize_t n=pread(fd,raw,(size_t)before.st_size,0);digest(raw,n>0?(size_t)n:0,sum);
  if(n!=before.st_size||strcmp(sum,PROBE_SHA256)||snprintf(path,sizeof path,"%s/probes/%s",AUTHORITY_ROOT,r->probe)>=(int)sizeof path){close(fd);close(probes);return 0;}
  int pipefd[2];if(pipe(pipefd)){close(fd);close(probes);return 0;}pid_t pid=fork();
  if(pid==0){close(pipefd[0]);if(dup2(pipefd[1],STDOUT_FILENO)<0)_exit(125);close(pipefd[1]);
    if(!drop_identity(uid,gid))_exit(125);static char *empty[]={NULL};environ=empty;setenv("PATH","/usr/bin:/bin",1);setenv("LANG","C",1);setenv("LC_ALL","C",1);setenv("HOME","/var/empty",1);execl(path,r->probe,(char*)NULL);_exit(125);}
  close(pipefd[1]);char output[256];size_t used=0;time_t deadline=time(NULL)+3;int status=0,done=0;
  fcntl(pipefd[0],F_SETFL,O_NONBLOCK);while(!done&&time(NULL)<=deadline){ssize_t q=read(pipefd[0],output+used,sizeof output-used-1);if(q>0)used+=(size_t)q;if(used>=sizeof output-1)break;pid_t w=waitpid(pid,&status,WNOHANG);if(w==pid)done=1;else usleep(10000);}
  if(!done){kill(pid,SIGKILL);waitpid(pid,&status,0);}for(;;){ssize_t q=read(pipefd[0],output+used,sizeof output-used-1);if(q<=0)break;used+=(size_t)q;if(used>=sizeof output-1)break;}close(pipefd[0]);output[used]=0;
  int stable=!fstat(fd,&after)&&same_stat(&before,&after)&&!fstatat(probes,r->probe,&current,AT_SYMLINK_NOFOLLOW)&&current.st_dev==after.st_dev&&current.st_ino==after.st_ino;close(fd);close(probes);
  char expected[256];int want=snprintf(expected,sizeof expected,"RESULT=%s\nEFFECT_MARKER=%s\n",r->result,r->marker);
  return done&&WIFEXITED(status)&&WEXITSTATUS(status)==0&&stable&&want>=0&&(size_t)want==used&&!memcmp(expected,output,used);
}
static int write_producer_evidence(const Request*r,uid_t uid,gid_t gid,const char *raw,size_t n){
  int root=root_fd(),dir=root<0?-1:child_dir(root,"evidence",uid);if(root>=0)close(root);if(dir<0)return 0;char name[80];snprintf(name,sizeof name,"%s.json",r->request_id);pid_t pid=fork();if(pid==0){if(!drop_identity(uid,gid))_exit(125);_exit(write_exact(dir,name,(const unsigned char*)raw,n,0444)?0:1);}int status;int ok=pid>0&&waitpid(pid,&status,0)==pid&&WIFEXITED(status)&&WEXITSTATUS(status)==0;close(dir);return ok;
}
static int producer(const Request*r){uid_t uid;gid_t gid;if(!producer_ids(&uid,&gid)||!run_probe(r,uid,gid))return 2;char receipt[DOC_MAX],evidence[DOC_MAX],effect[65];int rn=receipt_json(r,receipt,sizeof receipt);if(rn<=0||rn>=DOC_MAX)return 2;digest((unsigned char*)receipt,(size_t)rn,effect);int en=evidence_json(r,effect,evidence,sizeof evidence);if(en<=0||en>=DOC_MAX)return 2;if(!write_producer_evidence(r,uid,gid,evidence,(size_t)en))return 2;return printf("REQUEST_ID=%s\n",r->request_id)>0?0:2;}
static int observer(const Request*r){
  uid_t uid;gid_t gid;if(!producer_ids(&uid,&gid)||!exact_allowlist()||!run_probe(r,uid,gid))return 2;char receipt[DOC_MAX],evidence[DOC_MAX],token[DOC_MAX],effect[65],name[80];int rn=receipt_json(r,receipt,sizeof receipt);if(rn<=0||rn>=DOC_MAX)return 2;digest((unsigned char*)receipt,(size_t)rn,effect);int en=evidence_json(r,effect,evidence,sizeof evidence),tn=token_json(r,token,sizeof token);if(en<=0||en>=DOC_MAX||tn<=0||tn>=DOC_MAX)return 2;
  int root=root_fd(),edir=root<0?-1:child_dir(root,"evidence",uid),rdir=root<0?-1:child_dir(root,"probe-receipts",authority_uid()),state=root<0?-1:child_dir(root,"state",authority_uid()),pending=state<0?-1:child_dir(state,"pending",authority_uid());
  if(root>=0)close(root);if(state>=0)close(state);if(edir<0||rdir<0||pending<0){if(edir>=0)close(edir);if(rdir>=0)close(rdir);if(pending>=0)close(pending);return 2;}
  snprintf(name,sizeof name,"%s.json",r->request_id);unsigned char actual[DOC_MAX];size_t an=0;int ok=read_stable(edir,name,uid,actual,sizeof actual,&an)&&an==(size_t)en&&!memcmp(actual,evidence,an);
  if(ok)ok=write_exact(rdir,name,(unsigned char*)receipt,(size_t)rn,0444);if(ok)ok=write_exact(pending,name,(unsigned char*)token,(size_t)tn,0400);
  close(edir);close(rdir);close(pending);return ok?0:2;
}
static int consumer(const Request*r){
  char token[DOC_MAX],name[80];int tn=token_json(r,token,sizeof token);if(tn<=0||tn>=DOC_MAX)return 2;snprintf(name,sizeof name,"%s.json",r->request_id);
  int root=root_fd(),state=root<0?-1:child_dir(root,"state",authority_uid()),pending=state<0?-1:child_dir(state,"pending",authority_uid()),used=state<0?-1:child_dir(state,"used",authority_uid());if(root>=0)close(root);if(state>=0)close(state);if(pending<0||used<0){if(pending>=0)close(pending);if(used>=0)close(used);return 2;}
  unsigned char actual[DOC_MAX];size_t n=0;if(!read_stable(pending,name,authority_uid(),actual,sizeof actual,&n)){close(pending);close(used);return errno==ENOENT?1:2;}if(n!=(size_t)tn||memcmp(actual,token,n)){close(pending);close(used);return 1;}
  struct stat occupied;if(fstatat(used,name,&occupied,AT_SYMLINK_NOFOLLOW)==0||errno!=ENOENT){close(pending);close(used);return errno==ENOENT?2:1;}
  int ok=renameat(pending,name,used,name)==0;int saved=errno;close(pending);close(used);if(ok)return 0;return saved==ENOENT||saved==EEXIST?1:2;
}
int main(int argc,char **argv){
#ifndef NORTROPIC_FIXTURE
  if(geteuid()!=0)return 2;
#endif
  if(argc<1||!argv||!argv[0])return 2;char namebuf[PATH_MAX_LOCAL],generated[65]={0};if(strlen(argv[0])>=sizeof namebuf)return 2;strcpy(namebuf,argv[0]);const char *name=basename(namebuf);Request r={0};
  if(!strcmp(name,"request-producer")){if(!request_args(argc,argv,0,&r,generated))return 1;return producer(&r);}
  if(!strcmp(name,"request-observer")){if(!request_args(argc,argv,1,&r,generated))return 1;return observer(&r);}
  if(!strcmp(name,"request-consumer")){if(!request_args(argc,argv,2,&r,generated))return 1;return consumer(&r);}
  return 2;
}
