import React, { useState, useEffect } from 'react';

const Console = () => {
    const [logs, setLogs] = useState([]);

    useEffect(() => {
        const originalConsoleLog = console.log;
        console.log = (...args) => {
            setLogs((prevLogs) => [...prevLogs, args.join(' ')]);
            originalConsoleLog(...args);
        };

        return () => {
            console.log = originalConsoleLog;
        };
    }, []);

    return (
        <div style={{ backgroundColor: 'black', color: 'white', padding: '10px', maxHeight: '200px', overflowY: 'scroll' }}>
            {logs.map((log, index) => (
                <div key={index}>{log}</div>
            ))}
        </div>
    );
};

export default Console;