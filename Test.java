public class Test {
  private String str;

  public Test() {
    str = "hello world";
    System.out.println(str);
  }

  public static void main() {
    Test t = new Test();
    t.str = new String("good bye world");
    System.out.println(t.str.charAt(3));
  }
}