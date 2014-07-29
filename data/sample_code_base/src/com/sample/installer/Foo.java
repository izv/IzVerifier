
import com.izforge.izpack.installer.AutomatedInstallData;
import com.izforge.izpack.util.AbstractUIProcessHandler;
import com.izforge.izpack.util.VariableSubstitutor;

public Class Foo {

    public static void Run(AbstractUIProcessHandler handler, String [] args) {
        AutomatedInstallData idata = AutomatedInstallData.getInstance();

        String key1 = "some.string.1";
        String key2 = "some.string.4";
        String key3 = "some.string.6"
        String val = idata.langpack.getString(key1);
        setErrorMessageId("my.error.message.id.test");
        System.out.println("some.string.2");
        System.out.println(idata.langpack.getString(key2));
        System.out.println(idata.langpack.getString("some.string.3"));
        System.out.println(String.format(idata.langpack.getString("some.string.5")), string);
        System.out.println(String.format(idata.langpack.getString(key3)), string);
        System.out.println


        String cond1 = "some.condition.1";
        Boolean isTrue = idata.getRules().isConditionTrue(cond1);

        String someVar = "some.undefined.var.1";
        String someVal = idata.getVariable(someVar);

        String someVal2 = idata.getVariable("some.other.undefined.var");
    }

}