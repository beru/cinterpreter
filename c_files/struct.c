
#if 0

typedef struct B
{
	int a;
} B;

struct A
{
	B b;
	int a;
} as[] = {
	{{1}, 1},
	{{1}, 1},
};

struct A a;

#endif

int g_test;

int g_a = 0;
int g_b = 0;

int* g_ptr;
int g_arr[10];

struct A;

struct A
{
	char c;
/*
	int a;
	int b;
	int c;
	int* d;
	int* ips[10];
*/
};

struct
{
	int z;
	unsigned int ui;
	int unsigned ui2;
	long long ll;
	unsigned long long ull;
//	struct A c;
	int arr[10];
} a;

typedef struct {
	int a;
} B;

void structTest();

struct A g_a;

void structTest()
{
	struct A a;
	a.a = 0;
	
	B b;
	b.a = 10;
}

