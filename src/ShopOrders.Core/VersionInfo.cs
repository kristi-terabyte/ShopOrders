namespace ShopOrders.Core;

/// <summary>
/// Інформація про версію збірки (LR8).
/// </summary>
public static class VersionInfo
{
    /// <summary>
    /// Семантична версія навчального проєкту.
    /// </summary>
    public const string Version = "1.0.0";

    /// <summary>
    /// Кодова назва релізу.
    /// </summary>
    public const string Codename = "ShopOrders-Semester";

    /// <summary>
    /// Повертає рядок для відображення у консолі / CI.
    /// </summary>
    /// <returns>Версія та кодова назва.</returns>
    public static string GetDisplayString()
    {
        return $"{Codename} v{Version}";
    }
}
