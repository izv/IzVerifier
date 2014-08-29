
import com.izforge.izpack.installer.AutomatedInstallData;
import com.izforge.izpack.util.AbstractUIProcessHandler;
import com.izforge.izpack.util.VariableSubstitutor;

public Class Foo {

    public static void Run(AbstractUIProcessHandler handler, String [] args) {
        AutomatedInstallData idata = AutomatedInstallData.getInstance();
        Messages messages = idata.getMessages();

        String key1 = "some.string.1";
        String key2 = "some.string.4";
        String key3 = "some.string.6";

        String izpack5_test = idata.getMessages().get("my.izpack5.key");
        String izpack5_test2 = messages.get("my.izpack5.key.1");

        String errorMsgDup = idata.langpack.getString("hello.world");
        String val = idata.langpack.getString(key1);
        setErrorMessageId("my.error.message.id.test");
        System.out.println("some.string.2");
        System.out.println(idata.langpack.getString(key2));
        System.out.println(idata.langpack.getString("some.string.3"));
        System.out.println(String.format(idata.langpack.getString("some.string.5")), string);
        System.out.println(String.format(idata.langpack.getString(key3)), string);
        System.out.println(String.format(errorMsgDup,nameValuePair[0]));
        System.out.println(jdbcNameLbl + " " + idata.getVariable("db.driver"));


        String cond1 = "some.condition.1";
        Boolean isTrue = idata.getRules().isConditionTrue(cond1);
        Boolean isTrue2 = idata.getRules().isConditionTrue(and.2);
        Boolean isTrue3 = idata.getRules().isConditionTrue(or.cycle.1);

        String someVar = "some.undefined.var.1";
        String someVal = idata.getVariable(someVar);

        String someVal2 = idata.getVariable("some.other.undefined.var");
    }

}