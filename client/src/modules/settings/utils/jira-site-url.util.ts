export const normalizeJiraSiteUrl = (siteUrl: string): string => {
  return siteUrl.trim().replace(/\/+$/, "").toLowerCase();
};

export const checkIsSameJiraSite = (siteUrl: string, savedSiteUrl: string | null): boolean => {
  return (
    savedSiteUrl !== null && normalizeJiraSiteUrl(siteUrl) === normalizeJiraSiteUrl(savedSiteUrl)
  );
};
