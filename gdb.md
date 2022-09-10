
# gdb debug summary

set print pretty on

	1. bt
		1. bt full
	2. info threads
	3. info proc
		1. info proc stat
		2. info proc all
		3. info proc files
		4. info proc status
	4. x/32xg address
		1. 打印内存内容
	5. info locals
	6. info registers
	7. frame X (change to stack frame X)
	8. jemalloc
		1. arena
			1. p __je_narenas_auto  //arenas[0..narenas_auto)
			2. p narenas_total
			3. p __je_opt_narenas  // __je_ncpus *4
			4. p __je_arenas
			5. p __je_ncpus
			6. p huge_arena_ind
		2. tcache
			1. p __je_opt_tcache
			2. p __je_opt_lg_tcache_max  //15
			3. p *__je_tcache_bin_info
			4. p stack_nelms   //3096
			1. p __je_tcache_maxclass  //32768
			2. p __je_tcaches
			3. p tcaches_past
			4. p tcaches_avail
		1. debug
			1. p __je_opt_abort
			2. p __je_opt_junk_alloc
			3. p __je_opt_junk_free
		2. threads
			1. p __je_n_background_threads
			2. p __je_max_background_threads
		3. bin
			1. p __je_nhbins   //41
			2. p __je_bin_infos
		4. extent
			1. p extents_bitmap_info
			2. p __je_opt_retain
		5. size
			1. p __je_sz_pind2sz_tab
			2. p __je_sz_index2size_tab
			3. p __je_sz_size2index_tab


### 1) print data of some address
    x/32xg address
    examine命令缩写为x
    格式：
    x/<n/f/u> <addr>
    n:是正整数，表示需要显示的内存单元的个数，即从当前地址向后显示n个内存单元的内容，
    一个内存单元的大小由第三个参数u定义。

    f:表示addr指向的内存内容的输出格式，s对应输出字符串，此处需特别注意输出整型数据的格式：
    x 按十六进制格式显示变量.
    d 按十进制格式显示变量。
    u 按十进制格式显示无符号整型。
    o 按八进制格式显示变量。
    t 按二进制格式显示变量。
    a 按十六进制格式显示变量。
    c 按字符格式显示变量。
    f 按浮点数格式显示变量。

    u:就是指以多少个字节作为一个内存单元-unit,默认为4。u还可以用被一些字符表示:
    如b=1 byte, h=2 bytes,w=4 bytes,g=8 bytes.

    <addr>:表示内存地址。

### 2) show proc info (vm size)
    (gdb) info proc stat
    process 20424
    Name: isi_tardis_d
    Process ID: 20424
    Parent process: 1
    Process group: 20424
    Session id: 20424
    TTY: 18446744073709551615
    TTY owner process group: 0
    User IDs (real, effective, saved): 0 0 0
    Group IDs (real, effective, saved): 0 0 0
    Groups: 0
    Minor faults (no memory page): 256
    Minor faults, children: 0
    Major faults (memory page faults): 0
    Major faults, children: 0
    utime: 0.009997
    stime: 0.006506
    utime, children: 0.000000
    stime, children: 0.000000
    'nice' value: 0
    Start time: 1658389912.817907
    Virtual memory size: 1572132 kB
    Data size: 8 pages
    Stack size: 6208 pages
    Text size: 125 pages
    Resident set size: 327058 pages
    Maximum RSS: 788296 pages
    Ignored Signals: 187a9000 00000000 00000000 00000000
    Caught Signals: 80000000 00000000 00000020 01000000

### 2) bt full

### 3) info threads
    thread 3
