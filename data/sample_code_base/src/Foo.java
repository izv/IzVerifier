
import com.izforge.izpack.installer.AutomatedInstallData;
import com.izforge.izpack.util.AbstractUIProcessHandler;
import com.izforge.izpack.util.VariableSubstitutor;

public Class Foo {

    public static void Run(AbstractUIProcessHandler handler, String [] args) {
        AutomatedInstallData idata = AutomatedInstallData.getInstance();

        String key1 = "some.string.1";
        String key2 = "some.string.4";
        String val = idata.langpack.getString(key1);

        System.out.println("some.string.2");
        System.out.println(idata.langpack.getString(key2));
        System.out.println(idata.langpack.getString("some.string.3"));
    }

}