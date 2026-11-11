use proc_macro::TokenStream;

#[proc_macro]
pub fn forty_two(_: TokenStream) -> TokenStream {
    "42u64".parse().unwrap()
}
