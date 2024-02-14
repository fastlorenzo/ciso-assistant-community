import { expect, type Page } from './test-utils.js';
import { BasePage } from './base-page.js';

enum State {
    Unset = -1,
    False = 0,
    True = 1
}

export class LoginPage extends BasePage	{
    static readonly defaultEmail: string = 'admin@tests.com';
    static readonly defaultPassword: string = '1234';
    email: string;
    password: string;

    constructor(public readonly page: Page) {
        super(page, '/login', 'Login');
        this.email = LoginPage.defaultEmail;
        this.password = LoginPage.defaultPassword;
    }

    async login(email: string=LoginPage.defaultEmail, password: string=LoginPage.defaultPassword) {
        this.email = email;
        this.password = password;
        await this.page.locator('input[name="username"]').fill(email);
        await this.page.locator('input[name="password"]').fill(password);
        await this.page.getByRole('button', { name: 'Log in' }).click();
        if (email === LoginPage.defaultEmail && password === LoginPage.defaultPassword) {
            await this.page.waitForURL(/^.*\/((?!login).)*$/, { timeout: 10000 });
        }
        else {
            await this.page.waitForURL(/^.*\/login(\?next=\/.*)?$/);
        }
    }

    async hasUrl(redirect: State=State.Unset) {
        switch (redirect) {
            case State.Unset:
                // url can be /login or /login?next=/
                await expect(this.page).toHaveURL(/^.*\/login(\?next=\/.*)?$/);
                break;
            case State.False:
                // url must be /login
                await expect(this.page).toHaveURL(/^.*\/login$/);
                break;
            case State.True:
                //url must be /login?next=/
                await expect(this.page).toHaveURL(/^.*\/login\?next=\/.*$/);
                break;
        }
    }
}