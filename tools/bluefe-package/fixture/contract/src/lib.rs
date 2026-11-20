include!(concat!(env!("OUT_DIR"), "/generated.rs"));

/// ```
/// assert_eq!(bluefe_contract::answer(), 42);
/// ```
pub fn answer() -> u64 {
    bluefe_macros::forty_two!()
}

pub trait Value {
    fn value(&self) -> u64;
}

impl Value for u64 {
    fn value(&self) -> u64 { *self }
}

pub fn generic<T: Value>(value: &T) -> u64 {
    value.value()
}

pub fn dynamic(value: &dyn Value) -> u64 {
    value.value()
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::sync::Arc;
    use std::sync::atomic::{AtomicUsize, Ordering};

    #[test]
    fn generics_dynamic_dispatch_and_build_script() {
        assert_eq!(answer(), 42);
        assert_eq!(generic(&40u64) + GENERATED, answer());
        assert_eq!(dynamic(&42u64), answer());
        let values = [1u64, 2, 3];
        assert_eq!(values.iter().map(|value| value * value).sum::<u64>(), 14);
    }

    #[test]
    fn panic_unwinds_and_drops_exactly_once() {
        struct CountDrop(Arc<AtomicUsize>);
        impl Drop for CountDrop {
            fn drop(&mut self) { self.0.fetch_add(1, Ordering::SeqCst); }
        }
        let drops = Arc::new(AtomicUsize::new(0));
        let inside = drops.clone();
        let result = std::panic::catch_unwind(move || {
            let _owned = CountDrop(inside);
            panic!("qualification panic");
        });
        assert!(result.is_err());
        assert_eq!(drops.load(Ordering::SeqCst), 1);
    }

    #[test]
    fn thread_and_atomic_runtime() {
        let result = std::thread::spawn(answer).join().unwrap();
        assert_eq!(result, 42);
    }
}
