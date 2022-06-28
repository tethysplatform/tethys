describe('test.env', () => {
  it('TETHYS_DEBUG_MODE is defined', () => {
    expect(process.env.TETHYS_DEBUG_MODE).toBeDefined();
  });

  it('TETHYS_APP_ID is defined', () => {
    expect(process.env.TETHYS_APP_ID).toBeDefined();
  });

  it('TETHYS_APP_PACKAGE is defined', () => {
    expect(process.env.TETHYS_APP_PACKAGE).toBeDefined();
  });

  it('TETHYS_APP_ROOT_URL is defined', () => {
    expect(process.env.TETHYS_APP_ROOT_URL).toBeDefined();
  });

  it('TETHYS_LOADER_DELAY is defined', () => {
    expect(process.env.TETHYS_LOADER_DELAY).toBeDefined();
  });

  it('TETHYS_PORTAL_HOST is defined', () => {
    expect(process.env.TETHYS_PORTAL_HOST).toBeDefined();
  });
});