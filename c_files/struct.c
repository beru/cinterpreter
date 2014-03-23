
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

