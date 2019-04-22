void spin_lock(int *ptr) {
    // Assume the integer pointed to by ptr is initially 0
    while (!cas(ptr, 0, 1)) {
        // the cas trying to replace *ptr with 1
        // keep spinning if *ptr is already changed to 1 by other processes
    }
}

void spiin_unlock(int *ptr) {
    // reset the *ptr to 0 so that other process can acquire the lock
    cas(ptr, 1, 0)
}