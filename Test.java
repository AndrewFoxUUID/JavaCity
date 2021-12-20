public class Test {
  private Integer integer;

  public Test() {
    integer = new Integer(14);
    System.out.println(integer + 2);
    integer = 4;
  }

  public static void main() {
    Test t = new Test();
    t.integer = 2;
    System.out.println(t.integer + 1); // 3

    System.out.println(t.integer);
    t = new Test();
    System.out.println(t.integer);

    System.out.println(t.integer - 1); // 3
  }
}