type DateTime = string;

type LogLevel = string;

declare interface LogData {
    type: "log",
    message: string,
    level: LogLevel,
    time: DateTime
}

declare interface CheckData {
    type: "check",
    description: string,
    outcome: Boolean,
    details: string | null
}

declare interface AttachmentData {
    type: "attachment",
    filename: string,
    description: string
}

declare interface UrlData {
    type: "url",
    url: string,
    description: string
}

type StepEntryData = LogData | CheckData | AttachmentData | UrlData;

declare interface StepData {
    description: string,
    start_time: DateTime,
    end_time: DateTime | null,
    entries: Array<StepEntryData>;
}

declare interface HookData {
    start_time: DateTime,
    end_time: DateTime | null,
    outcome: Boolean,
    steps: Array<StepData>
}

type Status = string;

declare interface Link {
    name: string,
    url: string
}

declare interface BaseTestData {
    name: string,
    description: string,
    tags: Array<string>,
    properties: Array<object>,
    links: Array<Link>
}

declare interface TestData extends BaseTestData {
    start_time: DateTime,
    end_time: DateTime | null,
    steps: Array<StepData>,
    status: Status,
    status_details: string
}

declare interface SuiteData extends BaseTestData {
    tests: Array<TestData>,
    suites: Array<SuiteData>,
    suite_setup: HookData | undefined,
    suite_teardown: HookData | undefined
}

declare interface ReportData {
    title: string,
    start_time: DateTime,
    end_time: DateTime,
    generation_time: DateTime,
    info: Array<Array<string>>,
    stats: Array<Array<string>>,
    test_session_setup: HookData,
    test_session_teardown: HookData,
    suites: Array<SuiteData>
}