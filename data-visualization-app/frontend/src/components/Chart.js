import React, { useEffect, useState } from 'react';
import { Line } from 'react-chartjs-2';
import { fetchStatistics } from '../services/api';

const Chart = () => {
    const [data, setData] = useState({});
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            const result = await fetchStatistics();
            setData(result);
            setLoading(false);
        };

        fetchData();

        const interval = setInterval(() => {
            fetchData();
        }, 5000); // Fetch data every 5 seconds

        return () => clearInterval(interval);
    }, []);

    if (loading) {
        return <div>Loading...</div>;
    }

    return (
        <div>
            <h2>Statistics Chart</h2>
            <Line data={data} />
        </div>
    );
};

export default Chart;