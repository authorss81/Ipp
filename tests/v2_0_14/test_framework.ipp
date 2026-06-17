import { describe, it, expect, run_all } from "ipp-test"

describe("math utils", func() {
    it("adds two numbers", func() {
        expect(1 + 1).to_equal(2)
    })
    it("clamps correctly", func() {
        var clamp = func(v, lo, hi) { return v < lo ? lo : v > hi ? hi : v }
        expect(clamp(15, 0, 10)).to_equal(10)
        expect(clamp(-1, 0, 10)).to_equal(0)
        expect(clamp(5, 0, 10)).to_equal(5)
    })
    it("isclose works for floats", func() {
        expect(isclose(0.1 + 0.2, 0.3)).to_be_true()
    })
})

describe("string utils", func() {
    it("pads correctly", func() {
        expect("42".pad_left(5)).to_equal("   42")
    })
    it("detects digits", func() {
        expect("123".is_digit()).to_be_true()
        expect("12a".is_digit()).to_be_false()
    })
})

describe("error handling", func() {
    it("throws on nil access", func() {
        expect(func() {
            var x = nil
            print(x.field)
        }).to_throw()
    })
})

var ok = run_all()
assert ok == true
