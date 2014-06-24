
import com.izforge.izpack.installer.AutomatedInstallData;
import com.izforge.izpack.util.AbstractUIProcessHandler;
import com.izforge.izpack.util.VariableSubstitutor;

public Class Foo {

    public static void Run(AbstractUIProcessHandler handler, String [] args) {
        AutomatedInstallData idata = AutomatedInstallData.getInstance();

        String key = "some.string.2";

        System.out.println(idata.langpacks.getString(key));
        System.out.println(idata.langpacks.getString("some.string.1"));
    }

}